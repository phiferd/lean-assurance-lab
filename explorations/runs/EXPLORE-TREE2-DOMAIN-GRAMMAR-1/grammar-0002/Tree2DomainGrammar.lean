import Tree2ArrowTowerBridge

/- Local AI-authored symbolic-domain assessment. Prior sources are unchanged. -/
namespace Tree2DomainGrammar
open ConLeche Tree2Bridge Tree2TowerSupport

inductive Domain where
 | param
 | self
 | arrow (a b : Domain)
 deriving DecidableEq, Repr

namespace Domain
def hasSelf : Domain → Bool
 | .param => false
 | .self => true
 | .arrow a b => a.hasSelf || b.hasSelf

/-- Uniform parameter index shifts beneath every nondependent Pi. -/
def raw : Domain → Nat → Expr
 | .param,k => .bvar k
 | .self,k => t (.bvar k)
 | .arrow a b,k => pi (a.raw k) (b.raw (k+1))

/-- Instantiated, bound-variable-free interpretation, independently stated. -/
def encode (a x : Expr) : Domain → Expr
 | .param => a
 | .self => x
 | .arrow p q => arr (encode a x p) (encode a x q)

def official (d : Domain) := d.encode A tr
def native (d : Domain) := d.encode A X
def crest (d : Domain) := d.encode P Q
def height : Domain → Nat
 | .param | .self => 1
 | .arrow a b => max a.height b.height + 1
def sortLevel : Domain → Level
 | .param | .self => .succ .zero
 | .arrow a b => .imax a.sortLevel b.sortLevel

theorem raw_instantiate (d : Domain) (k : Nat) (v : Expr) :
 (d.raw k).instantiate1 v k = d.encode v (t v) := by
 induction d generalizing k with
 | param => simp [raw,encode,Expr.instantiate1]
 | self => simp [raw,encode,t,Expr.instantiate1]
 | arrow a b ia ib => simp only [raw,pi,Expr.instantiate1,encode,arr,ia,ib]

theorem encode_occ (d : Domain) (a x : Expr) (names : List Name) (lo hi : Nat)
 (ha : a.nestOcc names lo hi = false) (hx : x.nestOcc names lo hi = true) :
 (d.encode a x).nestOcc names lo hi = d.hasSelf := by
 induction d with
 | param => exact ha
 | self => exact hx
 | arrow p q ip iq => simp only [encode,arr,pi,Expr.nestOcc,hasSelf,ip,iq]

theorem native_occ (d : Domain) : (d.native).nestOcc [Tn] 1 2 = d.hasSelf :=
 encode_occ d A X [Tn] 1 2 (by rfl) (by rfl)

theorem official_occ (d : Domain) (names : List Name)
 (hn : names.contains Tn = true) :
 (d.official).nestOcc names 0 0 = d.hasSelf := by
 apply encode_occ d A tr names 0 0 (by rfl)
 simp only [tr,t,Expr.nestOcc,A,hn]
 rfl

theorem raw_occ (d : Domain) (k : Nat) (names : List Name)
 (hn : names.contains Tn = true) :
 (d.raw k).nestOcc names 0 0 = d.hasSelf := by
 induction d generalizing k with
 | param => rfl
 | self => simp only [raw,t,Expr.nestOcc,hasSelf,hn]; rfl
 | arrow a b ia ib => simp only [raw,pi,Expr.nestOcc,hasSelf,ia,ib]

theorem canonicalize (d : Domain) :
 (d.encode P (t P)).replaceApps (nestCanonSub [Tn] [] 1) 0 1 = d.crest := by
 induction d with
 | param => rfl
 | self => rfl
 | arrow a b ia ib => simp only [encode,arr,pi,Expr.replaceApps,crest,ia,ib]

theorem key_map (d : Domain) :
 (d.crest).replaceFVars (nestKeyMap [A] [X]) = d.native := by
 induction d with
 | param => rfl
 | self => rfl
 | arrow a b ia ib => simp only [crest,native,encode,arr,pi,Expr.replaceFVars] at *; rw [ia,ib]

theorem native_closed (d : Domain) : (d.native).bvarB = 0 := by
 induction d with
 | param => rfl
 | self => rfl
 | arrow a b ia ib => simp only [native,encode,arr,pi,Expr.bvarB_eq,Expr.bvarBound] at *; rw [ia,ib]; rfl

theorem native_range (d : Domain) : (d.native).fvarRange ≤ 2 := by
 induction d with
 | param => decide
 | self => decide
 | arrow a b ia ib => simp only [native,encode,arr,pi,Expr.fvarRange] at *; omega

theorem official_closed (d : Domain) : (d.official).bvarB = 0 := by
 induction d with
 | param => rfl
 | self => rfl
 | arrow a b ia ib => simp only [official,encode,arr,pi,Expr.bvarB_eq,Expr.bvarBound] at *; rw [ia,ib]; rfl

end Domain

#print axioms Domain.raw_instantiate
#print axioms Domain.native_occ
#print axioms Domain.official_occ
#print axioms Domain.canonicalize
#print axioms Domain.key_map
end Tree2DomainGrammar
