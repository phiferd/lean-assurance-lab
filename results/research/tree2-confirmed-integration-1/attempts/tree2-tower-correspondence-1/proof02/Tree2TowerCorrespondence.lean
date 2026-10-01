import Tree2TowerOfficial

/- Local AI-authored bounded representation proof; no upstream submission. -/
namespace Tree2TowerCorrespondence
open ConLeche Tree2Bridge Tree2TowerSupport Tree2TowerNative Tree2TowerOfficial
set_option maxRecDepth 3000
set_option maxHeartbeats 1000000

/-- Independent polynomial variables: row zero denotes the member. -/
inductive Slot where
 | parameter
 | row (depth : Nat)
 deriving DecidableEq, Repr
abbrev PolyRow := List Slot × Slot

def rootSignature (N : Nat) : List PolyRow :=
 [([.parameter],.row 0),([.row N],.row 0)]
def listSignature (j : Nat) : List PolyRow :=
 [([],.row j),([.row (j-1),.row j],.row j)]
def signature (N : Nat) : List (List PolyRow) :=
 rootSignature N :: (List.range N).map (fun i => listSignature (N-i))

/-- Reads the actual allocated numeric name and parameter, not an expected row. -/
def officialSlot (N : Nat) (e : Expr) : Option Slot :=
 if e == A then some .parameter else
 match e with
 | .app (.const name []) a =>
   if a == A then
    if name == Tn then some (.row 0) else
    match name with
    | .num pre i => if pre == nm "TowerAux" && (1 ≤ i && i ≤ N) then
                     some (.row (N-i+1)) else none
    | _ => none
   else none
 | _ => none

/-- Exact native member annotation and exact monomorphic List schema. -/
def towerDepth : Expr → Option Nat
 | .fvar 1 ty => if ty == S then some 0 else none
 | .app (.const name [.zero]) a =>
     if name == Ln then (towerDepth a).map Nat.succ else none
 | _ => none

/-- Raw index 2 is read only through its own actual key and base. -/
def nativeSlot (frame : Option NestHole) (e : Expr) : Option Slot :=
 if e == A then some .parameter else
 if e == Y then do
   let h ← frame
   if h.base == 2 then
     match h.key with
     | ⟨name,[.zero],[d]⟩ =>
       if name == Ln then return .row ((← towerDepth d)+1) else none
     | _ => none
   else none
 else (towerDepth e).map Slot.row

/-- Read fields/results from the actual crest; reject non-never binders. -/
def decodeRow (decode : Expr → Option Slot) : Expr → Option PolyRow
 | .forallE a b m => do
     if m == bm then
       let a' ← decode a
       let (bs,r) ← decodeRow decode b
       pure (a'::bs,r)
     else none
 | e => do let r ← decode e; pure ([],r)

def crestRows (frame : Option NestHole) (names : List Name) (us : List Level)
    (ds holes : List Expr) (cs : List (ConstantVal × Nat)) : List (Option PolyRow) :=
 cs.map fun (cv,_) =>
   (nestCrest names us ds holes (cv.type.instantiateLevelParams cv.levelParams us)).bind
     (decodeRow (nativeSlot frame))

def officialRows (N : Nat) : List (List (Option PolyRow)) :=
 (target N).types.toList.map fun ty => ty.ctors.map (decodeRow (officialSlot N))
def nativeRows (N : Nat) : List (List (Option PolyRow)) :=
 crestRows none [Tn] [] [A] [X] (roots N) ::
 (List.range N).map fun i =>
   crestRows (some (holeAt (N-i-1))) [Ln] [.zero] [tower (N-i-1)] [Y] listCs

theorem towerDepth_exact (k : Nat) : towerDepth (tower k) = some k := by
 induction k with
 | zero => rfl
 | succ k ih => simp [tower,l,towerDepth,ih]

theorem native_parameter (h : Option NestHole) : nativeSlot h A = some .parameter := rfl

theorem native_member_tower (h : Option NestHole) (k : Nat) :
 nativeSlot h (tower k) = some (.row k) := by
 cases k with
 | zero => rfl
 | succ k => simp [nativeSlot,tower,l,A,Y,towerDepth,towerDepth_exact]

theorem frame_self (k : Nat) :
 nativeSlot (some (holeAt k)) Y = some (.row (k+1)) := by
 simp [nativeSlot,Y,A,holeAt,towerKey,towerDepth_exact]

theorem unframed_self : nativeSlot none Y = none := rfl

theorem official_parameter (N : Nat) : officialSlot N A = some .parameter := rfl

theorem official_member (N : Nat) : officialSlot N tr = some (.row 0) := rfl

theorem official_aux (N i : Nat) (h1 : 1 ≤ i) (hN : i ≤ N) :
 officialSlot N (auxExpr i) = some (.row (N-i+1)) := by
 simp [officialSlot,auxExpr,freshName,A,Tn,nm,h1,hN]

theorem official_reference (N j : Nat) (hj : j ≤ N) :
 officialSlot N (R N j) = some (.row j) := by
 cases j with
 | zero => exact official_member N
 | succ j =>
   rw [signature_reference N (j+1) (by omega) hj,official_aux N _ (by omega) (by omega)]
   congr 2; omega

theorem decode_native_tower (h : Option NestHole) (k : Nat) :
 decodeRow (nativeSlot h) (tower k) = some ([],.row k) := by
 cases k with
 | zero => rfl
 | succ k => simp [tower,decodeRow,nativeSlot,towerDepth,towerDepth_exact,l,A,Y]

theorem decode_official_reference (N j : Nat) (hj : j ≤ N) :
 decodeRow (officialSlot N) (R N j) = some ([],.row j) := by
 cases j with
 | zero => rfl
 | succ j =>
   change (officialSlot N (R N (j+1))).bind _ = _
   rw [official_reference N (j+1) hj]
   rfl

theorem native_root_rows (N : Nat) :
 crestRows none [Tn] [] [A] [X] (roots N) = (rootSignature N).map some := by
 simp only [crestRows,roots,List.map_cons,List.map_nil]
 change [(nestCrest [Tn] [] [A] [X] leafCV.type).bind (decodeRow (nativeSlot none)),
   (nestCrest [Tn] [] [A] [X] ((node N).type.instantiateLevelParams [] [])).bind
      (decodeRow (nativeSlot none))] = _
 rw [root_crests.1,node_crest N]
 simp [rootSignature,decodeRow,arr,pi,native_parameter,native_member_tower,decode_native_tower,X]

theorem native_list_rows (k : Nat) :
 crestRows (some (holeAt k)) [Ln] [.zero] [tower k] [Y] listCs =
   (listSignature (k+1)).map some := by
 simp only [crestRows,listCs,List.map_cons,List.map_nil]
 change [(nestCrest [Ln] [.zero] [tower k] [Y]
   (nilCV.type.instantiateLevelParams [un] [.zero])).bind (decodeRow (nativeSlot (some (holeAt k)))),
   (nestCrest [Ln] [.zero] [tower k] [Y]
   (consCV.type.instantiateLevelParams [un] [.zero])).bind (decodeRow (nativeSlot (some (holeAt k))))] = _
 rw [(canonical_list_crest_substitution (tower k) Y).1,
     (canonical_list_crest_substitution (tower k) Y).2]
 simp [listSignature,decodeRow,arr,pi,frame_self,native_member_tower,decode_native_tower,Y]

theorem official_root_rows (N : Nat) :
 (rootRow N).ctors.map (decodeRow (officialSlot N)) = (rootSignature N).map some := by
 simp only [rootRow,rootSignature,List.map_cons,List.map_nil]
 change [decodeRow (officialSlot N) (arr A (R N 0)),
         decodeRow (officialSlot N) (arr (R N N) (R N 0))] = _
 simp [decodeRow,arr,pi,official_parameter,official_reference N N (Nat.le_refl N),
       decode_official_reference N 0 (Nat.zero_le N)]

theorem official_list_rows (N j : Nat) (hj : 1 ≤ j) (hN : j ≤ N) :
 (Tree2TowerOfficial.row N j).ctors.map (decodeRow (officialSlot N)) = (listSignature j).map some := by
 have hp : j-1 ≤ N := by omega
 simp [Tree2TowerOfficial.row,listSignature,decodeRow,arr,pi,
       official_reference N j hN,official_reference N (j-1) hp,
       decode_official_reference N j hN]


theorem native_interpretation (N : Nat) :
 nativeRows N = (signature N).map (List.map some) := by
 simp only [nativeRows,signature,List.map_cons,List.map_map,native_root_rows]
 congr 1
 apply List.map_congr_left
 intro i hi
 have hi' : i < N := List.mem_range.mp hi
 have he : N-i = (N-i-1)+1 := by omega
 change _ = (listSignature (N-i)).map some
 have h := native_list_rows (N-i-1)
 simpa only [he, Nat.add_sub_cancel] using h

theorem official_interpretation (N : Nat) :
 officialRows N = (signature N).map (List.map some) := by
 simp only [officialRows,target,List.toList_toArray,List.map_cons,List.map_map,
   signature,official_root_rows]
 congr 1
 apply List.map_congr_left
 intro i hi
 exact official_list_rows N (N-i) (by have := List.mem_range.mp hi; omega) (by omega)

#check native_interpretation
#check official_interpretation
#print axioms native_interpretation
#print axioms official_interpretation
end Tree2TowerCorrespondence
