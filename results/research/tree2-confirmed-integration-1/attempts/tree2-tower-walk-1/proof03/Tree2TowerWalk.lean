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

private theorem depthGo_sound (e : Expr) (m : Std.HashMap Expr Nat) (hm : MemoSound m) :
    (e.depthGo m).1 = height e ∧ MemoSound (e.depthGo m).2 := by
  induction e generalizing m with
  | bvar i => exact ⟨rfl,hm⟩
  | fvar i ty ih => exact ⟨rfl,hm⟩
  | sort u => exact ⟨rfl,hm⟩
  | const c us => exact ⟨rfl,hm⟩
  | lit v => exact ⟨rfl,hm⟩
  | app f a ihf iha =>
    rw [Expr.depthGo]
    split
    · exact ⟨hm _ _ ‹m[_]? = some _›,hm⟩
    · obtain ⟨hf,hfm⟩ := ihf m hm
      obtain ⟨ha,ham⟩ := iha (f.depthGo m).2 hfm
      simp only [hf,ha,height]
      exact ⟨rfl,memo_insert ham _⟩
  | lam a b meta iha ihb =>
    rw [Expr.depthGo]
    split
    · exact ⟨hm _ _ ‹m[_]? = some _›,hm⟩
    · obtain ⟨ha,ham⟩ := iha m hm
      obtain ⟨hb,hbm⟩ := ihb (a.depthGo m).2 ham
      simp only [ha,hb,height]
      exact ⟨rfl,memo_insert hbm _⟩
  | forallE a b meta iha ihb =>
    rw [Expr.depthGo]
    split
    · exact ⟨hm _ _ ‹m[_]? = some _›,hm⟩
    · obtain ⟨ha,ham⟩ := iha m hm
      obtain ⟨hb,hbm⟩ := ihb (a.depthGo m).2 ham
      simp only [ha,hb,height]
      exact ⟨rfl,memo_insert hbm _⟩
  | letE a v b iha ihv ihb =>
    rw [Expr.depthGo]
    split
    · exact ⟨hm _ _ ‹m[_]? = some _›,hm⟩
    · obtain ⟨ha,ham⟩ := iha m hm
      obtain ⟨hv,hvm⟩ := ihv (a.depthGo m).2 ham
      obtain ⟨hb,hbm⟩ := ihb (v.depthGo (a.depthGo m).2).2 hvm
      simp only [ha,hv,hb,height]
      exact ⟨rfl,memo_insert hbm _⟩
  | proj c i a iha =>
    rw [Expr.depthGo]
    split
    · exact ⟨hm _ _ ‹m[_]? = some _›,hm⟩
    · obtain ⟨ha,ham⟩ := iha m hm
      simp only [ha,height]
      exact ⟨rfl,memo_insert ham _⟩


#print axioms depthGo_sound
end Tree2TowerWalk
