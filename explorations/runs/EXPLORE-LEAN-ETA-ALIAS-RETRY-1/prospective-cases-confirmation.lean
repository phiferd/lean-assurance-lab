import Lean

open Lean Meta

structure Box where
  val : Bool

@[reducible] def FnAlias := Bool → Box

private def explicitType : Expr :=
  .forallE `_ (mkConst ``Bool) (mkConst ``Box) .default

private def aliasType : Expr :=
  .const ``FnAlias []

private def ctor : Expr :=
  .const ``Box.mk []

private def etaCtor : Expr :=
  .lam `b (mkConst ``Bool) (.app ctor (.bvar 0)) .default

private def showKernel : Except Kernel.Exception Bool → String
  | .ok value => toString value
  | .error _ => "error"

private def checkedType (label : String) (env : Environment) (lctx : LocalContext)
    (value : Expr) : MetaM Expr := do
  match Kernel.check env lctx value with
  | .ok type =>
      logInfo m!"{label} Kernel.check type={type}"
      return type
  | .error _ =>
      throwError "{label} Kernel.check failed"

private def assertExplicitFunctionType (type : Expr) : MetaM Unit := do
  match type with
  | .forallE _ domain body _ =>
      assert! domain == mkConst ``Bool
      assert! body == mkConst ``Box
  | _ =>
      throwError "expected a syntactic Bool-to-Box forall type"

private def observeNegative (label : String) (storedType : Expr) : MetaM Unit := do
  withLocalDeclD `f storedType fun f => do
    let env ← getEnv
    let lctx ← getLCtx
    let decl := lctx.get! f.fvarId!
    assert! decl.type == storedType
    assert! decl.value?.isNone
    assert! storedType == explicitType || storedType == aliasType
    assert! f.isFVar && !f.isLambda
    assert! ctor.isConst && !ctor.isLambda && ctor.getAppNumArgs == 0
    assert! f.getAppFn != ctor.getAppFn
    let lhsType ← checkedType (label ++ " lhs") env lctx f
    let rhsType ← checkedType (label ++ " rhs") env lctx ctor
    assert! lhsType == storedType
    assertExplicitFunctionType rhsType
    -- Observe the kernel first so Meta state or caching cannot affect it.
    let kernelResult := Kernel.isDefEq env lctx f ctor
    let metaResult ← isDefEq f ctor
    logInfo m!"{label}: expected=false meta={metaResult} kernel={showKernel kernelResult} storedType={decl.type} lhs={f} rhs={ctor}"

private def observePositive (label : String) (storedType : Expr) : MetaM Unit := do
  -- The unvalued context variable retains the explicit/alias fixture distinction.
  -- The compared lambda itself still infers a syntactic Pi, so this is an
  -- acceptance/control observation, not proof that the alias-sensitive branch ran.
  withLocalDeclD `context storedType fun context => do
    let env ← getEnv
    let lctx ← getLCtx
    let decl := lctx.get! context.fvarId!
    assert! decl.type == storedType
    assert! decl.value?.isNone
    assert! ctor.getAppNumArgs == 0
    let lhsType ← checkedType (label ++ " lhs") env lctx etaCtor
    let rhsType ← checkedType (label ++ " rhs") env lctx ctor
    assertExplicitFunctionType lhsType
    assertExplicitFunctionType rhsType
    let kernelResult := Kernel.isDefEq env lctx etaCtor ctor
    let metaResult ← isDefEq etaCtor ctor
    logInfo m!"{label}: expected=true meta={metaResult} kernel={showKernel kernelResult} storedType={decl.type} lhs={etaCtor} rhs={ctor}"

run_meta do
  logInfo m!"revision={Lean.githash}"
  observeNegative "explicit-negative" explicitType
  observeNegative "alias-negative" aliasType
  observePositive "explicit-constructor-positive" explicitType
  observePositive "alias-constructor-positive" aliasType
