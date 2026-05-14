import sys, types, os, io, contextlib
tk = types.ModuleType('tkinter')
class W:
    def __init__(self,*a,**k): pass
tk.Tk=W; tk.Canvas=W; tk.Frame=W; tk.Label=W; tk.Button=W; tk.ALL='all'; tk.NW='nw'
sys.modules['tkinter'] = tk
sys.modules['tkinter.ttk'] = types.ModuleType('tkinter.ttk')
from ipp.lexer.lexer import tokenize
from ipp.parser.parser import parse
from ipp.vm.compiler import compile_ast
from ipp.vm.vm import VM

TESTS = [
    ("v05","tests/v05/test_features.ipp"),
    ("v06","tests/v06/test_features.ipp"),
    ("v07","tests/v07/test_features.ipp"),
    ("v08","tests/v08/test_features.ipp"),
    ("v09","tests/v09/test_features.ipp"),
    ("v10","tests/v10/test_features.ipp"),
    ("v11","tests/v11/test_features.ipp"),
    ("v12","tests/v12/test_features.ipp"),
    ("v1.0","tests/v1/test_features.ipp"),
    ("v1.0.1","tests/v1_0_1/test_features.ipp"),
    ("v1.1.0","tests/v1_1_0/test_features.ipp"),
    ("v1.1.1","tests/v1_1_1/test_features.ipp"),
    ("v1.3.2","tests/v1_3_2/test_features.ipp"),
    ("v1.3.3","tests/v1_3_3/test_features.ipp"),
    ("v1.3.4-core","tests/v1_3_4/test_core_builtins.ipp"),
    ("v1.3.4-str","tests/v1_3_4/test_string_functions.ipp"),
    ("v1.3.4-fileio","tests/v1_3_4/test_file_io.ipp"),
    ("v1.3.4-datafmt","tests/v1_3_4/test_data_formats.ipp"),
    ("v1.3.4-math","tests/v1_3_4/test_math_library.ipp"),
    ("v1.3.4-coll","tests/v1_3_4/test_collections.ipp"),
    ("v1.3.4-adv","tests/v1_3_4/test_advanced_features.ipp"),
    ("v1.3.7-repl","tests/v1_3_7/test_repl_enhancements.ipp"),
    ("v1.3.7-vm","tests/v1_3_7/test_vm_bugs.ipp"),
    ("v1.3.8","tests/v1_3_8/test_networking_collections.ipp"),
    ("v1.3.9","tests/v1_3_9/test_error_handling.ipp"),
    ("v1.4.0","tests/v1_4_0/test_generators.ipp"),
    ("v1.5.0","tests/v1_5_0/test_additional_builtins.ipp"),
    ("v1.5.0-async","tests/v1_5_0/test_async_await.ipp"),
    ("v1.5.21","tests/v1_5_21/test_for_in_loop.ipp"),
    ("v1.5.22","tests/v1_5_22/test_pi_e_constants.ipp"),
    ("v1.5.23","tests/v1_5_23/test_let_immutable.ipp"),
    ("v1.5.24","tests/v1_5_24/test_str_method.ipp"),
    ("v1.5.25","tests/v1_5_25/test_static_methods.ipp"),
    ("v1.5.26","tests/v1_5_26/test_continue_while.ipp"),
    ("v1.5.27","tests/v1_5_27/test_continue_for.ipp"),
    ("v1.5.28","tests/v1_5_28/test_multi_var.ipp"),
    ("v1.5.29","tests/v1_5_29/test_list_comp.ipp"),
    ("v1.5.30","tests/v1_5_30/test_dict_comp.ipp"),
    ("v1.5.31","tests/v1_5_31/test_cache.ipp"),
    ("v1.5.32","tests/v1_5_32/test_set_index.ipp"),
    ("v1.5.33","tests/v1_5_33/test_do_while.ipp"),
    ("v1.5.34","tests/v1_5_34/test_multi_catch.ipp"),
    ("v1.5.35","tests/v1_5_35/test_variadic.ipp"),
    ("v1.5.36","tests/v1_5_36/test_fstrings.ipp"),
    ("v1.5.37","tests/v1_5_37/test_import.ipp"),
    ("v1.5.38","tests/v1_5_38/test_spread.ipp"),
    ("v1.6.0","tests/v1_6_0/test_operator_overload.ipp"),
    ("v1.6.1","tests/v1_6_1/test_exception_types.ipp"),
    ("v1.6.2","tests/v1_6_2/test_decorator.ipp"),
    ("v1.6.3","tests/v1_6_3/test_multi_return.ipp"),
    ("v1.6.4","tests/v1_6_4/test_named_args.ipp"),
    ("v1.6.5","tests/v1_6_5/test_property.ipp"),
    ("v1.6.6","tests/v1_6_6/test_signal.ipp"),
    ("v1.6.7","tests/v1_6_7/test_slicing.ipp"),
    ("v1.6.9","tests/v1_6_9/test_async.ipp"),
    ("v1.6.10","tests/v1_6_10/test_set.ipp"),
    ("v1.6.11","tests/v1_6_11/test_tailcall.ipp"),
    ("v1.6.12","tests/v1_6_12/test_fluent.ipp"),
    ("v1.6.13","tests/v1_6_13/test_string_format.ipp"),
    ("v1.6.14","tests/v1_6_14/test_bytecode_cache.ipp"),
    ("v1.7.1","tests/v1_7_1/test_opcodes.ipp"),
    ("v1.7.9-div","tests/v1_7_9/test_try_catch_div.ipp"),
    ("v1.7.9-idx","tests/v1_7_9/test_try_catch_index.ipp"),
    ("v1.7.9-nil","tests/v1_7_9/test_try_catch_nil.ipp"),
    ("v1.7.9-throw","tests/v1_7_9/test_try_catch_throw.ipp"),
    ("v1.7.8.1-basic","tests/v1_7_8_1/test_str_basic.ipp"),
    ("v1.7.8.1-concat","tests/v1_7_8_1/test_str_concat.ipp"),
    ("v1.7.8.1-inherit","tests/v1_7_8_1/test_str_inheritance.ipp"),
    ("v1.7.8.1-default","tests/v1_7_8_1/test_str_default.ipp"),
    ("v1.7.8.1-coll","tests/v1_7_8_1/test_str_collections.ipp"),
    ("v1.7.8.2-builtin","tests/v1_7_8_2/test_repr_builtin.ipp"),
    ("v1.7.8.2-method","tests/v1_7_8_2/test_repr_method.ipp"),
    ("v1.7.8.2-default","tests/v1_7_8_2/test_repr_default.ipp"),
    ("v1.7.8.2-coll","tests/v1_7_8_2/test_repr_collections.ipp"),
    ("v1.7.8.2-inherit","tests/v1_7_8_2/test_repr_inheritance.ipp"),
    ("v1.7.8.2-adv","tests/v1_7_8_2/test_repr_advanced.ipp"),
    ("v1.7.8.2-nested","tests/v1_7_8_2/test_repr_nested.ipp"),
    ("v1.7.8.2-coll-adv","tests/v1_7_8_2/test_repr_collections_adv.ipp"),
    ("v1.7.8.3-basic","tests/v1_7_8_3/test_len_basic.ipp"),
    ("v1.7.8.3-inherit","tests/v1_7_8_3/test_len_inheritance.ipp"),
    ("v1.7.8.3-default","tests/v1_7_8_3/test_len_default.ipp"),
    ("v1.7.6.2-dict-get","tests/v1_7_6_2/test_dict_get.ipp"),
]

passed=failed=0
failures=[]
for name,path in TESTS:
    if not os.path.exists(path):
        print(f"❌ {name}: FILE_NOT_FOUND"); failed+=1; failures.append((name,"FILE_NOT_FOUND")); continue
    try:
        vm=VM(); vm.run(compile_ast(parse(tokenize(open(path).read()))))
        print(f"✅ {name}"); passed+=1
    except Exception as e:
        msg=f"{type(e).__name__}: {str(e)[:80]}"
        print(f"❌ {name}: {msg}"); failed+=1; failures.append((name,msg))
print(f"\nPASSED:{passed} FAILED:{failed}")
for n,e in failures: print(f"  {n}: {e}")
