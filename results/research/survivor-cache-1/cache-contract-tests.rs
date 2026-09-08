
#[cfg(test)]
mod cache_contract_tests {
    use super::{Check, InferOnly};
    use crate::env::EnvLimit;
    use crate::pretty_printer::PpOptions;
    use crate::util::Config;
    use std::io::Cursor;

    const EMPTY_EXPORT: &[u8] = br#"{"meta":{"exporter":{"name":"lean4export","version":"3.1.0"},"format":{"version":"3.1.0"},"lean":{"githash":"985f350dcd18fc7814dfa677cac09933f44f3215","version":"4.29.0-rc1"}}}"#;

    fn run_checked_after_unchecked(candidate: bool) {
        let config = Config {
            export_file_path: None,
            use_stdin: true,
            permitted_axioms: Some(Vec::new()),
            unpermitted_axiom_hard_error: true,
            num_threads: 1,
            nat_extension: false,
            string_extension: false,
            pp_declars: None,
            unknown_pp_declar_hard_error: true,
            pp_options: PpOptions::default(),
            pp_output_path: None,
            pp_to_stdout: false,
            print_success_message: false,
            print_axioms: false,
            unsafe_permit_all_axioms: false,
        };
        let (export, skipped) = crate::parser::parse_export_file(Cursor::new(EMPTY_EXPORT), config)
            .expect("parse bound empty export");
        assert!(skipped.is_empty());
        export.with_tc(EnvLimit::Empty, |tc| {
            let zero = tc.ctx.zero();
            let one = tc.ctx.succ(zero);
            let sort0 = tc.ctx.mk_sort(zero);
            let sort1 = tc.ctx.mk_sort(one);
            let value = if candidate { sort1 } else { sort0 };
            let body = tc.ctx.mk_var(0);
            let name = tc.ctx.anonymous();
            let expression = tc.ctx.mk_let(name, sort1, value, body, false);
            let _ = tc.infer(expression, InferOnly);
            let _ = tc.infer(expression, Check);
        });
    }

    #[test]
    fn control() {
        run_checked_after_unchecked(false);
    }

    #[test]
    fn candidate() {
        let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            run_checked_after_unchecked(true);
        }));
        let payload = match result {
            Err(payload) => payload,
            Ok(()) => panic!("expected checked inference to reject warmed malformed let"),
        };
        let message = payload
            .downcast_ref::<String>()
            .map(String::as_str)
            .or_else(|| payload.downcast_ref::<&str>().copied())
            .expect("baseline panic payload must be a string");
        assert_eq!(message, "assertion failed: self.def_eq(u, v)");
    }
}
