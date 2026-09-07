import Lean4Lean.Verify.Level

/-!
CVC-2 specification proposal, not elaborated or proved in CVC-2.
Model CVC-U1: a single definition whose supplied value and declared type are
sorts. No proof replacement, environment extension, or importer correctness is
implied. Source correspondences and assumptions: contract.json and report.md
in results/research/conditional-validation-contracts/cvc-2/.
-/
namespace Lab.CVC2

inductive U where
  | zero : U
  | succ : U → U
  | max : U → U → U
  | imax : U → U → U
  | param : String → U
  deriving DecidableEq

-- This meaning is independent of Lean.Level and its comparison algorithm.
def meaning (ρ : String → Nat) : U → Nat
  | .zero => 0
  | .succ u => meaning ρ u + 1
  | .max u v => Nat.max (meaning ρ u) (meaning ρ v)
  | .imax u v => if meaning ρ v = 0 then 0 else Nat.max (meaning ρ u) (meaning ρ v)
  | .param n => ρ n

def Owned (params : List String) : U → Prop
  | .zero => True
  | .succ u => Owned params u
  | .max u v | .imax u v => Owned params u ∧ Owned params v
  | .param n => n ∈ params

structure SortDefinition where
  name : String
  params : List String
  valueLevel : U
  typeLevel : U

def Supported (a : SortDefinition) : Prop :=
  a.params.Nodup ∧ Owned a.params a.valueLevel ∧ Owned a.params a.typeLevel

-- The target judgment concerns the supplied Sort value, not existence of
-- another inhabitant of its declared type. No constants or axioms in the input.
def Contract (a : SortDefinition) : Prop :=
  Supported a ∧ ∀ ρ, meaning ρ a.valueLevel + 1 = meaning ρ a.typeLevel

def encode : U → Lean.Level
  | .zero => .zero
  | .succ u => .succ (encode u)
  | .max u v => .max (encode u) (encode v)
  | .imax u v => .imax (encode u) (encode v)
  | .param n => .param (.str .anonymous n)

def names (params : List String) : List Lean.Name :=
  params.map (fun n => .str .anonymous n)

-- S1 is the only selected strategy. Ownership precedes conversion/comparison.
-- Supported is a syntactic condition; it does not assume semantic validity.
def Accepts (a : SortDefinition) : Prop :=
  Supported a ∧ Lean.Level.isEquiv' (.succ (encode a.valueLevel)) (encode a.typeLevel) = true

-- Intermediate bridge to prove structurally, never an assumed axiom.
def EncodingTarget : Prop :=
  ∀ (params : List String) (u : U), params.Nodup → Owned params u →
    ∃ v, Lean4Lean.VLevel.ofLevel (names params) (encode u) = some v ∧
      v.WF params.length ∧
      ∀ ρ, v.eval (params.map ρ) = meaning ρ u

-- The single preservation target; the bridge and pinned comparator theorem
-- may be used to prove it. Neither is a premise of this proposition.
def PreservationTarget : Prop := ∀ a, Accepts a → Contract a

def rightSucc : SortDefinition :=
  ⟨"universeIMaxRightSucc", ["u", "v"],
   .imax (.param "u") (.succ (.param "v")),
   .succ (.max (.param "u") (.succ (.param "v")))⟩

def rightSuccControl : SortDefinition :=
  ⟨"universeIMaxRightSuccControl", ["u", "v"],
   .max (.param "u") (.succ (.param "v")),
   .succ (.max (.param "u") (.succ (.param "v")))⟩

-- Well-formed but invalid at ρ("u") = 1: the two sides are 1 and 2.
def zeroBoundary : SortDefinition :=
  ⟨"cvc2ZeroBoundary", ["u"], .imax (.param "u") .zero, .succ (.param "u")⟩

-- Algebraic equality alone is insufficient: "u" is unowned here.
def unownedBoundary : SortDefinition :=
  ⟨"cvc2UnownedBoundary", ["v"], .param "u", .succ (.param "u")⟩

-- Finite acceptance promise. No completeness promise over all Supported inputs.
def AcceptanceTarget : Prop := Accepts rightSucc ∧ Accepts rightSuccControl

def BoundaryTarget : Prop :=
  Supported zeroBoundary ∧ ¬ Contract zeroBoundary ∧ ¬ Accepts zeroBoundary ∧
  ¬ Supported unownedBoundary ∧ ¬ Accepts unownedBoundary

end Lab.CVC2
