# v2.0.8.4: story {} narrative branching syntax

var dialogue_log = []

func show_dialogue(speaker, text) {
    dialogue_log.append(speaker + ": " + text)
}

# ===== npc dialogue =====
story greet {
    npc "Guard": "Halt! Who goes there?"
    npc "Guard": "Pass, friend."
}

run_story(greet)
print("dialog len: " + str(len(dialogue_log)))
assert len(dialogue_log) == 2
assert dialogue_log[0] == "Guard: Halt! Who goes there?"
print("a ok")
assert dialogue_log[1] == "Guard: Pass, friend."
print("b ok")

# ===== story with flag =====
story flag_test {
    npc "Elara": "Take this torch."
    flag has_torch = true
}

run_story(flag_test)
print("c: len=" + str(len(dialogue_log)))
assert len(dialogue_log) == 3
assert dialogue_log[2] == "Elara: Take this torch."
print("d ok")
print("flag: " + str(story_flag("has_torch")))
assert story_flag("has_torch") == true
print("e ok")

# ===== story is a reusable value =====
run_story(greet)
print("f: len=" + str(len(dialogue_log)))
assert len(dialogue_log) == 5
assert dialogue_log[3] == "Guard: Halt! Who goes there?"
print("g ok")
assert dialogue_log[4] == "Guard: Pass, friend."
print("h ok")

# ===== choice with flag dispatch (user-defined show_choice) =====
var choice_log = []

func show_choice(...args) {
    choice_log.append("called")
    return 0
}

story choose_first {
    choice {
        "opt A" => { flag picked_a = true }
        "opt B" => { flag picked_b = true }
    }
}

run_story(choose_first)
print("i: choices=" + str(len(choice_log)))
assert len(choice_log) == 1
print("j ok")
print("picked_a: " + str(story_flag("picked_a")))
assert story_flag("picked_a") == true
print("k ok")

# ===== scene transition =====
var scene_log = []

func scene_transition(name) {
    scene_log.append(name)
}

story scene_test {
    npc "Guide": "Follow me."
    scene "forest"
    npc "Guide": "We are here."
}

run_story(scene_test)
print("l: scenes=" + str(len(scene_log)))
assert len(scene_log) == 1
assert scene_log[0] == "forest"
print("m ok")

# ===== label and goto =====
var goto_log = []

func set_story_goto(label_name) {
    goto_log.append(label_name)
}

story goto_test {
    npc "A": "Start"
    goto skip_part
    npc "B": "This should be skipped"
    label skip_part
    npc "C": "After skip"
}

run_story(goto_test)
print("n: gotos=" + str(len(goto_log)))
assert len(goto_log) == 1
assert goto_log[0] == "skip_part"
print("o ok")

print("All v2.0.8.4 story tests passed!")
