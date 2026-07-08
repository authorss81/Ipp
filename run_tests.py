import sys, types, os, io, contextlib

_orig_print = print
def _safe_print(*args, **kwargs):
    """Print with encoding fallback for Windows cp1252 consoles."""
    text = ' '.join(str(a) for a in args)
    try:
        _orig_print(text, **kwargs)
    except UnicodeEncodeError:
        cleaned = text.encode('ascii', errors='replace').decode('ascii')
        _orig_print(cleaned, **kwargs)
print = _safe_print
tk = types.ModuleType('tkinter')
class W:
    def __init__(self,*a,**k): pass
    def title(self,*a,**k): pass
    def geometry(self,*a,**k): pass
    def protocol(self,*a,**k): pass
    def resizable(self,*a,**k): pass
    def config(self,*a,**k): pass
    def cget(self, *a): return "580" if a and a[0] == "width" else ("380" if a and a[0] == "height" else "0")
    def pack(self,*a,**k): pass
    def update_idletasks(self,*a,**k): pass
    def update(self,*a,**k): pass
    def destroy(self): pass
    def after_cancel(self,*a,**k): pass
    def create_rectangle(self,*a,**k): pass
    def create_oval(self,*a,**k): pass
    def create_line(self,*a,**k): pass
    def create_text(self,*a,**k): pass
    def delete(self,*a,**k): pass
    def bind(self,*a,**k): pass
    def after(self,*a,**k): return "job"
tk.Tk=W; tk.Canvas=W; tk.Frame=W; tk.Label=W; tk.Button=W; tk.ALL='all'; tk.NW='nw'
sys.modules['tkinter'] = tk
sys.modules['tkinter.ttk'] = types.ModuleType('tkinter.ttk')
from ipp.lexer.lexer import tokenize
from ipp.parser.parser import parse
from ipp.vm.compiler import compile_ast
from ipp.vm.vm import VM

ipp_dir = os.path.dirname(os.path.abspath(__file__))

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
    ("v1.7.9.1.12-isclose","tests/v1_7_9_1_12/test_isclose.ipp"),
    ("v1.7.9.1.13-class-field-err","tests/v1_7_9_1_13/test_class_field_error.ipp"),
    ("v1.7.9.1.14-trunc-floor","tests/v1_7_9_1_14/test_trunc_floor.ipp"),
    ("v1.7.9.1.15-closure-loop","tests/v1_7_9_1_15/test_closure_loop.ipp"),
    ("v1.7.9.1.16-class-fields","tests/v1_7_9_1_16/test_class_fields.ipp"),
    ("v1.7.9.1.17-assert-msg","tests/v1_7_9_1_17/test_assert_msg.ipp"),
    ("v1.8.0-str-methods","tests/v1_8_0/test_string_methods.ipp"),
    ("v1.8.0.1-str-format","tests/v1_8_0_1/test_str_format.ipp"),
    ("v1.8.0.2-str-search","tests/v1_8_0_2/test_str_search.ipp"),
    ("v1.8.0.3-str-repeat","tests/v1_8_0_3/test_str_repeat.ipp"),
    ("v1.8.0.4-str-padding","tests/v1_8_0_4/test_str_padding.ipp"),
    ("v1.8.0.5-str-predicates","tests/v1_8_0_5/test_str_predicates.ipp"),
    ("v1.8.1-variadic","tests/v1_8_1/test_variadic_fix.ipp"),
    ("v1.8.1.1-list-mutation","tests/v1_8_1_1/test_list_mutation.ipp"),
    ("v1.8.1.2-list-aggregates","tests/v1_8_1_2/test_list_aggregates.ipp"),
    ("v1.8.1.3-list-transforms","tests/v1_8_1_3/test_list_transforms.ipp"),
    ("v1.8.1.4-list-search","tests/v1_8_1_4/test_list_search.ipp"),
    ("v1.8.2-multi-assign","tests/v1_8_2/test_multi_assign.ipp"),
    ("v1.8.2.1-swap","tests/v1_8_2_1/test_swap.ipp"),
    ("v1.8.3-map-filter-reduce","tests/v1_8_3/test_fluent_real.ipp"),
    ("v1.8.3.1-list-advanced","tests/v1_8_3_1/test_list_advanced.ipp"),
    ("v1.8.4-set-len","tests/v1_8_4/test_set_len.ipp"),
    ("v1.8.5-vec-arithmetic","tests/v1_8_5/test_vec_arithmetic.ipp"),
    ("v1.8.6-spread","tests/v1_8_6/test_spread.ipp"),
    ("v1.8.6.1-dict-spread","tests/v1_8_6_1/test_dict_spread.ipp"),
    ("v1.8.7-prop-basic","tests/v1_8_7/test_prop_basic.ipp"),
    ("v1.8.7-prop-edge","tests/v1_8_7/test_prop_edge.ipp"),
    ("v1.8.8-is","tests/v1_8_8/test_is_operator.ipp"),
    ("v1.9.0-slice","tests/v1_9_0/test_slice_syntax.ipp"),
    ("v1.9.0.1-slice-step","tests/v1_9_0_1/test_slice_step.ipp"),
    ("v1.9.1-global","tests/v1_9_1/test_global_keyword.ipp"),
    ("v1.9.1.1-nonlocal","tests/v1_9_1_1/test_nonlocal.ipp"),
    ("v1.9.2-map-filter-reduce","tests/v1_9_2/test_map_filter_reduce.ipp"),
    ("v1.9.3-multiline-strings","tests/v1_9_3/test_multiline_strings.ipp"),
    ("v1.9.4-async-return","tests/v1_9_4/test_async_return.ipp"),
    ("v1.9.5-set-ops","tests/v1_9_5/test_set_ops.ipp"),
    ("v1.9.5.1-set-comprehension","tests/v1_9_5_1/test_set_comprehension.ipp"),
    ("v1.9.6-lazy-range-enumerate","tests/v1_9_6/test_lazy_range_enumerate.ipp"),
    ("v1.9.7-zip","tests/v1_9_7/test_zip.ipp"),
    ("v1.9.8-sorted","tests/v1_9_8/test_sorted.ipp"),
    ("v1.9.9-dict-full","tests/v1_9_9/test_dict_full.ipp"),
    ("v1.9.12-export","tests/v1_9_12/test_export.ipp"),
    ("v1.9.13-project-mode","tests/v1_9_13/test_project_mode/test_project.ipp"),
    ("v2.0.0-game-loop","tests/v2_0_0/test_game_loop.ipp"),
    ("v2.1.0-keyboard","tests/v2_1_0/test_keyboard.ipp"),
    ("v2.2.0-canvas","tests/v2_2_0/test_canvas.ipp"),
    ("v2.3.0-audio","tests/v2_3_0/test_audio.ipp"),
    ("v2.4.0-network","tests/v2_4_0/test_network.ipp"),
    ("v2.0.0.1-time","tests/v2_0_0_1/test_time.ipp"),
    ("v2.0.0.2-draw-stubs","tests/v2_0_0_2/test_draw_stubs.ipp"),
    ("v2.0.0.3-enum","tests/v2_0_0_3/test_enum.ipp"),
    ("v2.0.0.4-schedule","tests/v2_0_0_4/test_schedule.ipp"),
    ("v2.0.0.5-invariant","tests/v2_0_0_5/test_invariant.ipp"),
    ("v2.0.1-input","tests/v2_0_1/test_input_headless.ipp"),
    ("v2.0.1.1-mouse","tests/v2_0_1_1/test_mouse_input.ipp"),
    ("v2.0.1.2-inspect","tests/v2_0_1_2/test_inspect.ipp"),
    ("v2.0.2-export","tests/v2_0_2/test_export.ipp"),
    ("v2.0.2.1-export-hints","tests/v2_0_2_1/test_export_hints.ipp"),
    ("v2.0.3-list-destruct","tests/v2_0_3/test_list_destructure.ipp"),
    ("v2.0.3.1-dict-destruct","tests/v2_0_3_1/test_dict_destructure.ipp"),
    ("v2.0.4-type-match","tests/v2_0_4/test_type_match.ipp"),
    ("v2.0.5-fstring-format","tests/v2_0_5/test_fstring_format.ipp"),
    ("v2.0.6-template-strings","tests/v2_0_6/test_template_strings.ipp"),
    ("v2.0.7-list-guard-match","tests/v2_0_7/test_pattern_match.ipp"),
    ("v2.0.7.1-dict-match","tests/v2_0_7.1/test_dict_match.ipp"),
    ("v2.0.8-tween","tests/v2_0_8/test_tween.ipp"),
    ("v2.0.8.2-parallel","tests/v2_0_8_2/test_parallel.ipp"),
    ("v2.0.8.3-sequence","tests/v2_0_8_3/test_sequence.ipp"),
    ("v2.0.8.4-story","tests/v2_0_8_4/test_story.ipp"),
    ("v2.0.9-scene-tree","tests/v2_0_9/test_scene_tree.ipp"),
    ("v2.0.10-resource-mgr","tests/v2_0_10/test_resource_manager.ipp"),
    ("v2.0.11-ecs","tests/v2_0_11/test_ecs.ipp"),
    ("v2.0.12-io","tests/v2_0_12/test_io.ipp"),
    ("v2.0.13-log","tests/v2_0_13/test_log.ipp"),
    ("v2.0.14-test","tests/v2_0_14/test_framework.ipp"),
    ("v2.0.15-math2d","tests/v2_0_15/test_math2d.ipp"),
    ("v2.0.16-random","tests/v2_0_16/test_random.ipp"),
    ("v2.0.17-collections","tests/v2_0_17/test_collections.ipp"),
    ("v2.0.18-signal","tests/v2_0_18/test_signal.ipp"),
    ("v2.0.19-ai","tests/v2_0_19/test_ai.ipp"),
    ("v2.0.19.1-pool","tests/v2_0_19_1/test_pool.ipp"),
    ("v2.0.19.2-timer","tests/v2_0_19_2/test_timer.ipp"),
    ("v2.0.19.3-net","tests/v2_0_19_3/test_net.ipp"),
    ("v2.0.20-canvas","tests/v2_0_20/test_canvas.ipp"),
    ("v2.0.20.1-canvas-sprites","tests/v2_0_20_1/test_canvas_sprites.ipp"),
    ("v2.0.20.2-tilemap","tests/v2_0_20_2/test_tilemap.ipp"),
    ("v2.0.20.3-assert-frame","tests/v2_0_20_3/test_assert_frame.ipp"),
    ("v2.0.20.4-resource-annotations","tests/v2_0_20_4/test_resource_annotations.ipp"),
    ("v2.0.21-ipp-ui","tests/v2_0_21/test_ui.ipp"),
    ("v2.0.22-gpu","tests/v2_0_22/test_gpu.ipp"),
    ("v2.0.23-physics","tests/v2_0_23/test_physics.ipp"),
    ("v2.0.24-audio","tests/v2_0_24/test_audio_real.ipp"),
    ("v2.0.25-debugger","tests/v2_0_25/test_debugger.ipp"),
    ("v2.0.25-debugger-loop","tests/v2_0_25/test_debugger_loop.ipp"),
    ("v2.0.25-debugger-nested","tests/v2_0_25/test_debugger_nested.ipp"),
    ("v2.0.25-debugger-class","tests/v2_0_25/test_debugger_class.ipp"),
    ("v2.0.25-debugger-if","tests/v2_0_25/test_debugger_if.ipp"),
    ("v2.0.25-debugger-multi","tests/v2_0_25/test_debugger_multi.ipp"),
    ("v2.0.25-repl-improvements","tests/v2_0_25/test_repl_improvements.py"),
    ("v2.1.0-inspect","tests/v2_1_0/test_inspect.ipp"),
    ("v2.1.0.1-default-vm","tests/v2_1_0_1/test_default_vm.py"),
    ("v2.1.0.2.1-banner","tests/v2_1_0_2_1/test_banner_mode.py"),
    ("v2.1.0.2.2-no-ippc","tests/v2_1_0_2_2/test_no_ippc.py"),
    ("v2.1.0.2.3-types-import","tests/v2_1_0_2_3/test_types_import.py"),
    ("v2.1.0.2.3-types-behavior","tests/v2_1_0_2_3/test_types_behavior.ipp"),
]

passed=failed=0
failures=[]
for name,path in TESTS:
    if not os.path.exists(path):
        print(f"[FAIL] {name}: FILE_NOT_FOUND"); failed+=1; failures.append((name,"FILE_NOT_FOUND")); continue
    try:
        if path.endswith('.py'):
            import subprocess
            r = subprocess.run([sys.executable, path], capture_output=True, text=True, cwd=ipp_dir)
            if r.returncode == 0:
                print(f"[PASS] {name}"); passed+=1
            else:
                err = r.stderr.strip()[:80] if r.stderr.strip() else r.stdout.strip()[:80]
                print(f"[FAIL] {name}: {err}"); failed+=1; failures.append((name, err))
            if r.stdout.strip():
                print(r.stdout.strip())
        else:
            vm=VM(); vm._current_source_file=os.path.abspath(path)
            # v2.0.25: supply canned "continue" input for debugger tests
            if name.startswith("v2.0.25-debugger"):
                responses = iter(["continue"] * 100)
                vm._debug_input_fn = lambda prompt="", it=responses: next(it)
            vm.run(compile_ast(parse(tokenize(open(path).read()))))
            print(f"[PASS] {name}"); passed+=1
    except Exception as e:
        msg=f"{type(e).__name__}: {str(e)[:80]}"
        print(f"[FAIL] {name}: {msg}"); failed+=1; failures.append((name,msg))
print(f"\nPASSED:{passed} FAILED:{failed}")
for n,e in failures: print(f"  {n}: {e}")
