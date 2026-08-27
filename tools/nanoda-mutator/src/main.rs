use proc_macro2::{LineColumn, Span};
use serde::Serialize;
use std::{env, fs, path::PathBuf};
use syn::{spanned::Spanned, visit::Visit, BinOp, Expr, ImplItemFn, ItemFn, Stmt};

#[derive(Serialize)]
struct Candidate {
    line_start: usize,
    line_end: usize,
    column_start: usize,
    operator: &'static str,
    family: &'static str,
    subsystem: &'static str,
    function: Option<String>,
    rationale: &'static str,
    original: String,
    mutated: String,
}

struct Collector<'a> {
    source: &'a str,
    line_offsets: Vec<usize>,
    candidates: Vec<Candidate>,
    current_function: Option<String>,
}

impl<'a> Collector<'a> {
    fn offset(&self, position: LineColumn) -> usize {
        self.line_offsets[position.line - 1] + position.column
    }

    fn text(&self, span: Span) -> String {
        let start = span.start();
        let end = span.end();
        self.source[self.offset(start)..self.offset(end)].to_string()
    }

    fn add(
        &mut self,
        span: Span,
        operator: &'static str,
        family: &'static str,
        subsystem: &'static str,
        rationale: &'static str,
        original: String,
        mutated: String,
    ) {
        let start = span.start();
        let end = span.end();
        self.candidates.push(Candidate {
            line_start: start.line,
            line_end: end.line,
            column_start: start.column,
            operator,
            family,
            subsystem,
            function: self.current_function.clone(),
            rationale,
            original,
            mutated,
        });
    }

    fn add_skip_validation(&mut self, span: Span, subsystem: &'static str) {
        let original = self.text(span);
        let mutated = format!("if false {{ {original} }}");
        self.add(
            span,
            "SKIP_VALIDATION",
            "validation-elision",
            subsystem,
            "Models omission of a semantic validation call.",
            original,
            mutated,
        );
    }
}

impl<'ast> Visit<'ast> for Collector<'_> {
    fn visit_item_fn(&mut self, node: &'ast ItemFn) {
        let previous = self.current_function.replace(node.sig.ident.to_string());
        syn::visit::visit_item_fn(self, node);
        self.current_function = previous;
    }

    fn visit_impl_item_fn(&mut self, node: &'ast ImplItemFn) {
        let previous = self.current_function.replace(node.sig.ident.to_string());
        syn::visit::visit_impl_item_fn(self, node);
        self.current_function = previous;
    }

    fn visit_stmt(&mut self, stmt: &'ast Stmt) {
        if let Stmt::Macro(stmt_macro) = stmt {
            if stmt_macro.mac.path.is_ident("assert") {
                let tokens = stmt_macro.mac.tokens.to_string();
                let subsystem = if tokens.contains("uparam") || tokens.contains("level") {
                    "universes"
                } else {
                    "serialized-input-validation"
                };
                self.add_skip_validation(stmt.span(), subsystem);
            }
        }
        if let Stmt::Expr(expr, Some(_)) = stmt {
            match expr {
                Expr::MethodCall(call) => {
                    let method = call.method.to_string();
                    let classification = match method.as_str() {
                        "assert_def_eq" => Some(("SKIP_VALIDATION", "definitional-equality")),
                        "infer_sort_of" => Some(("SKIP_VALIDATION", "declaration-validation")),
                        "check_declar" | "check_declar_info" => {
                            Some(("SKIP_VALIDATION", "declaration-validation"))
                        }
                        _ => None,
                    };
                    if let Some((operator, subsystem)) = classification {
                        debug_assert_eq!(operator, "SKIP_VALIDATION");
                        self.add_skip_validation(stmt.span(), subsystem);
                    }
                }
                Expr::Macro(expr_macro) if expr_macro.mac.path.is_ident("assert") => {
                    let tokens = expr_macro.mac.tokens.to_string();
                    let subsystem = if tokens.contains("uparam") || tokens.contains("level") {
                        "universes"
                    } else {
                        "serialized-input-validation"
                    };
                    self.add_skip_validation(stmt.span(), subsystem);
                }
                _ => {}
            }
        }
        syn::visit::visit_stmt(self, stmt);
    }

    fn visit_expr_if(&mut self, expr_if: &'ast syn::ExprIf) {
        if !matches!(&*expr_if.cond, Expr::Let(_) | Expr::Lit(_)) {
            let span = expr_if.cond.span();
            let original = self.text(span);
            let mutated = format!("!({original})");
            self.add(
                span,
                "BOOL_NEGATE",
                "predicate-negation",
                "unknown",
                "Models an inverted semantic guard or validation predicate.",
                original,
                mutated,
            );
        }
        syn::visit::visit_expr_if(self, expr_if);
    }

    fn visit_expr_binary(&mut self, binary: &'ast syn::ExprBinary) {
        if matches!(binary.op, BinOp::Add(_))
            && matches!(
                &*binary.right,
                Expr::Lit(expr_lit)
                    if matches!(&expr_lit.lit, syn::Lit::Int(value) if value.base10_digits() == "1")
            )
        {
            let span = binary.span();
            let original = self.text(span);
            let mutated = format!("({} + 0)", self.text(binary.left.span()));
            self.add(
                span,
                "BINDER_DEPTH_INCREMENT_ZERO",
                "binder-depth-adjustment",
                "unknown",
                "Models failure to increase de Bruijn depth when entering a binder.",
                original,
                mutated,
            );
        }
        let mutation = match binary.op {
            BinOp::Eq(_) => Some(("REL_EQ_TO_NE", "!=", "equality-discrimination")),
            BinOp::Ne(_) => Some(("REL_NE_TO_EQ", "==", "equality-discrimination")),
            BinOp::Lt(_) => Some(("REL_LT_TO_LE", "<=", "relational-boundary")),
            BinOp::Le(_) => Some(("REL_LE_TO_LT", "<", "relational-boundary")),
            BinOp::Gt(_) => Some(("REL_GT_TO_GE", ">=", "relational-boundary")),
            BinOp::Ge(_) => Some(("REL_GE_TO_GT", ">", "relational-boundary")),
            _ => None,
        };
        if let Some((operator, replacement, family)) = mutation {
            let span = binary.span();
            let original = self.text(span);
            let op_start = self.offset(binary.op.span().start()) - self.offset(span.start());
            let op_end = self.offset(binary.op.span().end()) - self.offset(span.start());
            let mut changed = original.clone();
            changed.replace_range(op_start..op_end, replacement);
            let mutated = format!("({changed})");
            self.add(
                span,
                operator,
                family,
                "unknown",
                "Models an equality or boundary-check error in semantic validation.",
                original,
                mutated,
            );
        }
        syn::visit::visit_expr_binary(self, binary);
    }
}

fn main() {
    let path = env::args_os().nth(1).map(PathBuf::from).unwrap_or_else(|| {
        eprintln!("usage: nanoda-mutator SOURCE.rs");
        std::process::exit(2);
    });
    let source = fs::read_to_string(&path).unwrap_or_else(|error| {
        eprintln!("{}: {error}", path.display());
        std::process::exit(1);
    });
    let syntax = syn::parse_file(&source).unwrap_or_else(|error| {
        eprintln!("{}: {error}", path.display());
        std::process::exit(1);
    });
    let mut line_offsets = vec![0];
    for (index, byte) in source.bytes().enumerate() {
        if byte == b'\n' {
            line_offsets.push(index + 1);
        }
    }
    let mut collector = Collector {
        source: &source,
        line_offsets,
        candidates: Vec::new(),
        current_function: None,
    };
    collector.visit_file(&syntax);
    collector
        .candidates
        .sort_by_key(|candidate| (candidate.line_start, candidate.column_start));
    println!(
        "{}",
        serde_json::to_string_pretty(&collector.candidates).unwrap()
    );
}

#[cfg(test)]
mod tests {
    use super::*;

    fn collect(source: &str) -> Vec<Candidate> {
        let syntax = syn::parse_file(source).unwrap();
        let mut line_offsets = vec![0];
        for (index, byte) in source.bytes().enumerate() {
            if byte == b'\n' {
                line_offsets.push(index + 1);
            }
        }
        let mut collector = Collector {
            source,
            line_offsets,
            candidates: Vec::new(),
            current_function: None,
        };
        collector.visit_file(&syntax);
        collector.candidates
    }

    #[test]
    fn emits_binder_depth_increment_elision() {
        let candidates = collect("fn inst_aux(offset: u16) { let next = offset + 1; }");
        let candidate = candidates
            .iter()
            .find(|row| row.operator == "BINDER_DEPTH_INCREMENT_ZERO")
            .unwrap();
        assert_eq!(candidate.function.as_deref(), Some("inst_aux"));
        assert_eq!(candidate.original, "offset + 1");
        assert_eq!(candidate.mutated, "(offset + 0)");
    }

    #[test]
    fn ignores_non_unit_addition() {
        let candidates = collect("fn inst_aux(offset: u16) { let next = offset + 2; }");
        assert!(candidates
            .iter()
            .all(|row| row.operator != "BINDER_DEPTH_INCREMENT_ZERO"));
    }
}
