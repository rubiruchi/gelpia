#!/usr/bin/env python3

import collections # OrderedDict
import sys         # exit

from pass_utils import *
from expression_walker import no_mut_walk


def reverse_diff(exp, inputs, assigns, consts=None):
  """
  Performs reverse accumulated automatic differentiation of the given exp
    for all variables
  """

  # Constants
  UNUSED = {"Const", "ConstantInterval", "PointInterval", "Integer", "Float"}
  POWS   = {"pow", "powi"}

  # Function local variables
  gradient = collections.OrderedDict([(k,("Integer","0")) for k in inputs])
  seen_undiff = False


  def _input(work_stack, count, exp):
    assert(exp[0] == "Input")
    old = gradient[exp[1]]
    if old == ("Integer", "0"):
      gradient[exp[1]] = exp[-1]
    else:
      gradient[exp[1]] = ("+", old, exp[-1])


    # All the cases for supported operators

  def _add(work_stack, count, exp):
    assert(exp[0] == "+")
    assert(len(exp) == 4)
    work_stack.append((False, count, (*exp[1], exp[-1])))
    work_stack.append((False, count, (*exp[2], exp[-1])))


  def _sub(work_stack, count, exp):
    assert(exp[0] == "-")
    assert(len(exp) == 4)
    work_stack.append((False, count, (*exp[1], exp[-1])))
    work_stack.append((False, count, (*exp[2], ("neg", exp[-1]))))


  def _mul(work_stack, count, exp):
    assert(exp[0] == "*")
    assert(len(exp) == 4)
    left = exp[1]
    right = exp[2]
    work_stack.append((False, count, (*exp[1], ("*", exp[-1], right))))
    work_stack.append((False, count, (*exp[2], ("*", exp[-1], left))))


  def _div(work_stack, count, exp):
    assert(exp[0] == "/")
    assert(len(exp) == 4)
    upper = exp[1]
    lower = exp[2]
    work_stack.append((False, count, (*exp[1], ("/", exp[-1], lower))))
    work_stack.append((False, count, (*exp[2], ("/", ("*", ("neg", exp[-1]), upper), ("pow", lower, ("Integer", "2"))))))


  def _pow(work_stack,count, exp):
    assert(exp[0] in {"pow", "powi"})
    assert(len(exp) == 4)
    base = exp[1]
    expo = exp[2]
    work_stack.append((False, count, (*exp[1], ("*", exp[-1], ("*", expo, ("powi", base, ("-", expo, ("Integer", "1"))))))))
    work_stack.append((False, count, (*exp[2], ("*", exp[-1], ("*", ("log", base), ("powi", base, expo))))))


  def _neg(work_stack, count, exp):
    assert(exp[0] == "neg")
    assert(len(exp) == 3)
    work_stack.append((False, count, (*exp[1], ("neg", exp[-1]))))


  def _exp(work_stack, count, exp):
    assert(exp[0] == "exp")
    assert(len(exp) == 3)
    expo = exp[1]
    work_stack.append((False, count, (*exp[1], ("*", ("exp", expo), exp[-1]))))


  def _log(work_stack, count, exp):
    assert(exp[0] == "log")
    assert(len(exp) == 3)
    base = exp[1]
    work_stack.append((False, count, (*exp[1], ("/", exp[-1], base))))


  def _sqrt(work_stack, count, exp):
    assert(exp[0] == "sqrt")
    assert(len(exp) == 3)
    x = exp[1]
    work_stack.append((False, count, (*exp[1], ("/", exp[-1], ("*", ("Integer", "2"), ("sqrt", x))))))


  def _cos(work_stack, count, exp):
    assert(exp[0] == "cos")
    assert(len(exp) == 3)
    x = exp[1]
    work_stack.append((False, count, (*exp[1], ("*", ("neg", ("sin", x)), exp[-1]))))


  def _acos(work_stack, count, exp):
    assert(exp[0] == "acos")
    assert(len(exp) == 3)
    x = exp[1]
    work_stack.append((False, count, (*exp[1], ("neg", ("/", exp[-1], ("sqrt", ("-", ("Integer", "1"), ("pow", x, ("Integer", "2")))))))))


  def _sin(work_stack, count, exp):
    assert(exp[0] == "sin")
    assert(len(exp) == 3)
    x = exp[1]
    work_stack.append((False, count, (*exp[1], ("*", ("cos", x), exp[-1]))))


  def _asin(work_stack, count, exp):
    assert(exp[0] == "asin")
    assert(len(exp) == 3)
    x = exp[1]
    work_stack.append((False, count, (*exp[1], ("/", exp[-1], ("sqrt", ("-", ("Integer", "1"), ("pow", x, ("Integer", "2"))))))))


  def _tan(work_stack, count, exp):
    assert(exp[0] == "tan")
    assert(len(exp) == 3)
    x = exp[1]
    work_stack.append((False, count, (*exp[1], ("*", ("+", ("Integer", "1"), ("pow", ("tan", x), ("Integer", "2"))), exp[-1]))))


  def _atan(work_stack, count, exp):
    assert(exp[0] == "atan")
    assert(len(exp) == 3)
    x = exp[1]
    work_stack.append((False, count, (*exp[1], ("/", exp[-1], ("+", ("Integer", "1"), ("pow", x, ("Integer", "2")))))))


  def _cosh(work_stack, count, exp):
    assert(exp[0] == "cosh")
    assert(len(exp) == 3)
    x = exp[1]
    work_stack.append((False, count, (*exp[1], ("*", ("sinh", x), exp[-1]))))


  def _sinh(work_stack, count, exp):
    assert(exp[0] == "sinh")
    assert(len(exp) == 3)
    x = exp[1]
    work_stack.append((False, count, (*exp[1], ("*", ("cosh", x), exp[-1]))))


  def _asinh(work_stack, count, exp):
    assert(exp[0] == "asinh")
    assert(len(exp) == 3)
    x = exp[1]
    work_stack.append((False, count, (*exp[1], ("/", exp[-1], ("sqrt", ("+", ("pow", x, ("Integer", "2")), ("Integer", "1")))))))


  def _tanh(work_stack, count, exp):
    assert(exp[0] == "tanh")
    assert(len(exp) == 3)
    x = exp[1]
    work_stack.append((False, count, (*exp[1], ("*", ("-", ("Integer", "1"), ("pow", ("tanh", x), ("Integer", "2"))), exp[-1]))))


  def _abs(work_stack, count, exp):
    assert(exp[0] == "abs")
    assert(len(exp) == 3)
    x = exp[1]
    work_stack.append((False, count, (*exp[1], ("*", ("dabs", x), exp[-1]))))


  # Recur
  def _variable(work_stack, count, exp):
    assert(exp[0] == "Variable")
    assert(len(exp) == 3)
    work_stack.append((False, count, (*assigns[exp[1]], exp[-1])))


  def _undiff(work_stack, count, exp):
    nonlocal seen_undiff
    assert(exp[0] == "floor_power2" or exp[0] == "sym_interval" or exp[0] == "sub2" or exp[0] == "sub2_I")
    seen_undiff = True
    work_stack.append((True, 0, "Return"))
    work_stack.append((True, 1, "Now"))

  my_expand_dict = {"Input": _input,
                    "+": _add,
                    "-": _sub,
                    "*": _mul,
                    "/": _div,
                    "pow": _pow,
                    "powi": _pow,
                    "neg": _neg,
                    "exp": _exp,
                    "log": _log,
                    "sqrt": _sqrt,
                    "cos": _cos,
                    "acos": _acos,
                    "sin": _sin,
                    "asin": _asin,
                    "tan": _tan,
                    "atan": _atan,
                    "cosh": _cosh,
                    "sinh": _sinh,
                    "asinh": _asinh,
                    "tanh": _tanh,
                    "abs": _abs,
                    "Variable": _variable,
                    "floor_power2": _undiff,
                    "sym_interval": _undiff}

  no_mut_walk(my_expand_dict, (*exp[1], ("Integer", "1")), assigns)

  if seen_undiff:
    result = ("Box",)
  else:
    result = ("Box",) + tuple(d for d in gradient.values())
  retval = ("Return", ("Tuple", exp[1], result))

  return retval








def runmain():
  from lexed_to_parsed import parse_function
  from pass_lift_inputs_and_assigns import lift_inputs_and_assigns
  from pass_lift_consts import lift_consts
  from pass_dead_removal import dead_removal
  from pass_simplify import simplify
  from output_rust import to_rust
  from pass_single_assignment import single_assignment

  data = get_runmain_input()
  exp = parse_function(data)
  exp, inputs, assigns = lift_inputs_and_assigns(exp)
  e, exp, consts = lift_consts(exp, inputs, assigns)
  dead_removal(exp, inputs, assigns, consts)

  exp = reverse_diff(exp, inputs, assigns, consts)
  exp = simplify(exp, inputs, assigns, consts)

  if len(sys.argv) == 3 and sys.argv[2] == "test":
    assert(exp[0] == "Return")
    tup = exp[1]
    assert(tup[0] == "Tuple")
    box = tup[2]
    if box[0] == "Const":
      const = box
      assert(const[0] == "Const")
      box = expand(const, assigns, consts)

    assert(box[0] == "Box")
    if len(box) == 1:
      print("No input variables")
      assert(len(inputs) == 0)
      return

    for name, diff in zip(inputs.keys(), box[1:]):
        print("d{} = {}".format(name, expand(diff, assigns, consts)))

  else:
    single_assignment(exp, inputs, assigns, consts)
    print("reverse_diff:")
    print_exp(exp)
    print()
    print_inputs(inputs)
    print()
    print_consts(consts)
    print()
    print_assigns(assigns)


if __name__ == "__main__":
  try:
    runmain()
  except KeyboardInterrupt:
    print("\nGoodbye")
