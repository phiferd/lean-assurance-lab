import Tree2TowerNative
import Std.Data.HashMap.Lemmas

/- Local AI-authored exploratory automatic walk connection. No upstream submission. -/
namespace Tree2TowerWalk
open ConLeche Tree2Bridge Tree2TowerSupport Tree2TowerNative
set_option maxRecDepth 2000
set_option maxHeartbeats 1000000

/- Local memo accounting, used only to bound the real upstream depth.
   No property of a replacement depth function is assumed. -/
private def height : Expr → Nat
  | .app f a => max (height f) (height a) + 1
  | .lam a b _ | .forallE a b _ => max (height a) (height b) + 1
  | .letE a v b => max (max (height a) (height v)) (height b) + 1
  | .proj _ _ a => height a + 1
  | _ => 1

private def MemoSound (m : Std.HashMap Expr Nat) : Prop :=
  ∀ e r, m[e]? = some r → r = height e

private theorem memo_insert {m : Std.HashMap Expr Nat} (hm : MemoSound m) (e : Expr) :
    MemoSound (m.insert e (height e)) := by
  intro a r hr
  rw [Std.HashMap.getElem?_insert] at hr
  split at hr
  · have h : e = a := by simpa using ‹(e == a) = true›
    subst a
    exact Option.some.inj hr.symm
  · exact hm a r hr


#print axioms memo_insert
end Tree2TowerWalk
