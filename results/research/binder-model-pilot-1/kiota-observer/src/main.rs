use kiota::expr::{self, BinderInfo, Expr, ExprData};
use kiota::level;
use serde_json::{json, Value};
use std::env;
use std::fs::File;
use std::io::{BufRead, BufReader, BufWriter, Write};

fn array<'a>(value: &'a Value, label: &str) -> Result<&'a Vec<Value>, String> {
    value.as_array().ok_or_else(|| format!("{label} must be an array"))
}

fn unsigned(value: &Value, label: &str) -> Result<u32, String> {
    let n = value.as_u64().ok_or_else(|| format!("{label} must be a nonnegative integer"))?;
    u32::try_from(n).map_err(|_| format!("{label} exceeds u32"))
}

fn member<'a>(value: &'a Value, key: &str) -> Result<&'a Value, String> {
    value.get(key).ok_or_else(|| format!("missing {key}"))
}

fn number(value: &Value, key: &str) -> Result<u32, String> {
    unsigned(member(value, key)?, key)
}

fn decode(value: &Value) -> Result<Expr, String> {
    let a = array(value, "expression")?;
    let tag = a.first().and_then(Value::as_str).ok_or("missing expression tag")?;
    match tag {
        "b" if a.len() == 2 => Ok(expr::bvar(unsigned(&a[1], "bvar index")?)),
        "s" if a.len() == 1 => Ok(expr::sort(level::zero())),
        "a" if a.len() == 3 => Ok(expr::app(decode(&a[1])?, decode(&a[2])?)),
        "l" if a.len() == 3 => Ok(expr::lam(BinderInfo::Default, decode(&a[1])?, decode(&a[2])?)),
        "t" if a.len() == 4 => Ok(expr::let_(decode(&a[1])?, decode(&a[2])?, decode(&a[3])?)),
        _ => Err("unsupported expression tag or arity".to_owned()),
    }
}

fn encode(e: &Expr) -> Result<Value, String> {
    match &***e {
        ExprData::BVar(i) => Ok(json!(["b", i])),
        ExprData::Sort(l) if matches!(&**l, level::LevelData::Zero) => Ok(json!(["s"])),
        ExprData::App(f, a) => Ok(json!(["a", encode(f)?, encode(a)?])),
        ExprData::Lam(BinderInfo::Default, t, b) => Ok(json!(["l", encode(t)?, encode(b)?])),
        ExprData::Let(t, v, b) => Ok(json!(["t", encode(t)?, encode(v)?, encode(b)?])),
        _ => Err("selected API returned expression outside fragment".to_owned()),
    }
}

fn observe(value: &Value) -> Result<Value, String> {
    let id = member(value, "id")?.as_str().ok_or("id must be string")?;
    let op = member(value, "operation")?.as_str().ok_or("operation must be string")?;
    let source = decode(member(value, "source")?)?;
    let args = array(member(value, "arguments")?, "arguments")?;
    let p = member(value, "parameters")?;
    let outputs = match op {
        "LIFT" => {
            if !args.is_empty() { return Err("lift argument count".to_owned()); }
            vec![encode(&expr::shift(&source, number(p, "d")? as i32, number(p, "s")?))?]
        }
        "SUBST" => {
            if args.len() != 1 { return Err("subst argument count".to_owned()); }
            vec![encode(&expr::instantiate1(&source, &decode(&args[0])?))?]
        }
        "LIFT_COMPOSE" => {
            if !args.is_empty() { return Err("lift composition argument count".to_owned()); }
            let first = expr::shift(&source, number(p, "d1")? as i32, number(p, "s1")?);
            let second = expr::shift(&first, number(p, "d2")? as i32, number(p, "s2")?);
            vec![encode(&first)?, encode(&second)?]
        }
        "SUBST_COMPOSE" => {
            if args.len() != 2 { return Err("subst composition argument count".to_owned()); }
            let first = expr::instantiate1(&source, &decode(&args[0])?);
            let second = expr::instantiate1(&first, &decode(&args[1])?);
            vec![encode(&first)?, encode(&second)?]
        }
        _ => return Err("unsupported operation".to_owned()),
    };
    Ok(json!({"id": id, "outputs": outputs}))
}

fn run(path: &str) -> Result<(), String> {
    let file = File::open(path).map_err(|e| e.to_string())?;
    let mut out = BufWriter::new(std::io::stdout().lock());
    for (line_number, line) in BufReader::new(file).lines().enumerate() {
        let line = line.map_err(|e| e.to_string())?;
        if line.is_empty() { return Err(format!("blank line {}", line_number + 1)); }
        let value: Value = serde_json::from_str(&line).map_err(|e| e.to_string())?;
        expr::clear_subst_memos();
        let observed = observe(&value)?;
        writeln!(out, "{}", observed).map_err(|e| e.to_string())?;
    }
    out.flush().map_err(|e| e.to_string())
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let result = if args.len() == 2 { run(&args[1]) } else { Err("expected one NDJSON path".to_owned()) };
    if let Err(error) = result {
        eprintln!("binder observer: {error}");
        std::process::exit(1);
    }
}
