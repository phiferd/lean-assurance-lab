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
  | .error error => s!"error: {error}"

private def observeNegative (label : String) (storedType : Expr) : MetaM Unit := do
  withLocalDeclD `f storedType fun f => do
    let lctx ← getLCtx
    let decl := lctx.get! f.fvarId!
    assert! decl.type == storedType
    assert! decl.value?.isNone
    assert! storedType == explicitType || storedType == aliasType
    assert! f.isFVar && !f.isLambda
    assert! ctor.isConst && !ctor.isLambda && ctor.getAppNumArgs == 0
    assert! f.getAppFn != ctor.getAppFn
    -- Observe the kernel first so Meta state or caching cannot affect it.
    let kernel := Kernel.isDefEq (← getEnv) lctx f ctor
    let meta ← isDefEq f ctor
    logInfo m!"{label}: expected=false meta={meta} kernel={showKernel kernel} storedType={decl.type} lhs={f} rhs={ctor}"

private def observePositive (label : String) (storedType : Expr) : MetaM Unit := do
  -- The unvalued context variable retains the explicit/alias fixture distinction.
  -- The compared lambda itself still infers a syntactic Pi, so this is an
  -- acceptance/control observation, not proof that the alias-sensitive branch ran.
  withLocalDeclD `context storedType fun context => do
    let lctx ← getLCtx
    let decl := lctx.get! context.fvarId!
    assert! decl.type == storedType
    assert! decl.value?.isNone
    assert! ctor.getAppNumArgs == 0
    let kernel := Kernel.isDefEq (← getEnv) lctx etaCtor ctor
    let meta ← isDefEq etaCtor ctor
    logInfo m!"{label}: expected=true meta={meta} kernel={showKernel kernel} storedType={decl.type} lhs={etaCtor} rhs={ctor}"

run_meta do
  observeNegative "explicit-negative" explicitType
  observeNegative "alias-negative" aliasType
  observePositive "explicit-constructor-positive" explicitType
  observePositive "alias-constructor-positive" aliasType
