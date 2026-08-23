use proc_macro2::{LineColumn, Span};
use serde::Serialize;
use std::{env, fs, path::PathBuf};
use syn::{spanned::Spanned, visit::Visit, Expr, Stmt};

#[derive(Serialize)]
struct Candidate {
    line_start: usize,
    line_end: usize,
    column_start: usize,
    operator: &'static str,
    subsystem: &'static str,
    original: String,
    mutated: String,
}

struct Collector<'a> {
    source: &'a str,
    line_offsets: Vec<usize>,
    candidates: Vec<Candidate>,
}

impl<'a> Collector<'a> {
    fn offset(&self, position: LineColumn) -> usize {
        self.line_offsets[position.line - 1] + position.column
    }

    fn add(&mut self, span: Span, operator: &'static str, subsystem: &'static str) {
        let start = span.start();
        let end = span.end();
        let original = self.source[self.offset(start)..self.offset(end)].to_string();
        self.candidates.push(Candidate {
            line_start: start.line,
            line_end: end.line,
            column_start: start.column,
            operator,
            subsystem,
            mutated: format!("if false {{ {original} }}"),
            original,
        });
    }
}

impl<'ast> Visit<'ast> for Collector<'_> {
    fn visit_stmt(&mut self, stmt: &'ast Stmt) {
        if let Stmt::Macro(stmt_macro) = stmt {
            if stmt_macro.mac.path.is_ident("assert") {
                let tokens = stmt_macro.mac.tokens.to_string();
                let subsystem = if tokens.contains("uparam") || tokens.contains("level") {
                    "universes"
                } else {
                    "serialized-input-validation"
                };
                self.add(stmt.span(), "SKIP_VALIDATION", subsystem);
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
                        self.add(stmt.span(), operator, subsystem);
                    }
                }
                Expr::Macro(expr_macro) if expr_macro.mac.path.is_ident("assert") => {
                    let tokens = expr_macro.mac.tokens.to_string();
                    let subsystem = if tokens.contains("uparam") || tokens.contains("level") {
                        "universes"
                    } else {
                        "serialized-input-validation"
                    };
                    self.add(stmt.span(), "SKIP_VALIDATION", subsystem);
                }
                _ => {}
            }
        }
        syn::visit::visit_stmt(self, stmt);
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
