import re
import os
import sys
import fileinput
import platform

# consider --help
# consider input from file?
# consider output to given file?
# consider option for dep if you know this is done in commands
# 

file_pattern = "[`'](.+)['']."
start_target_pattern = " *Considering target file " + file_pattern
pruning_pattern = " *Pruning file " + file_pattern
end_target_pattern = " *Successfully remade target file " + file_pattern
no_remake_pattern = " *No need to remake target " + file_pattern
no_remake_vpath_pattern = " *No need to remake target " + file_pattern+"; using VPATH name " + file_pattern
command_pattern = " *Must remake target " + file_pattern

cmd_builtins=("CD", "CHDIR", "COPY", "DEL", "ERASE", "DIR", "MD", "MKDIR", "PATH",
              "REN", "RENAME", "RD", "RMDIR", "CLS", "ECHO", "EXIT", "TYPE", "DATE",
              "TIME", "BREAK", "CALL", "CHCP", "FOR", "GOTO", "IF", "PAUSE", "PROMPT",
              "REM", "SET", "SHIFT", "VER", "VERIFY", "VOL")

def from_lines(lines):
    target_stack = []
    target_map = {}
    target_commands = {}
    target_sorted = []
    target_path = {}

    while len(lines) > 0:
        line = lines.pop()

        # add target
        match = re.search(start_target_pattern, line)
        if match != None:
            target_name = match.group(1)

            if len(target_stack) > 0:
                target_map[target_stack[-1]].append(target_name)

            target_stack.append(target_name)
            target_map[target_name] = []
            target_commands[target_name] = []

            target_sorted.append(target_name)
            continue
        
        # pruning file, add it as a dep to current target
        match = re.search(pruning_pattern, line)
        if match != None:
            assert len(target_stack) > 0

            target_name = target_stack[-1]
            dep = match.group(1)
            if (target_name != dep):
                target_map[target_name].append(dep)

            continue

        # remove target, built
        match = re.search(end_target_pattern, line)
        if match != None:
            target_name = match.group(1)
            removed_target = target_stack.pop()
            continue

        # remove target, no need to build, with VPATH
        match = re.search(no_remake_vpath_pattern, line)
        if match != None:
            target_stack.pop()
            target_name = match.group(1)
            path = match.group(2)
            target_path[target_name] = path
            continue

        # remove target, no need to build
        match = re.search(no_remake_pattern, line)
        if match != None:
            target_stack.pop()
            continue

        # rebuild target, with command following
        match = re.search(command_pattern, line)
        if match != None:
            assert len(target_stack) > 0

            target_name = target_stack[-1]

            while len(lines) > 0 and not lines[-1].startswith(" ") and not lines[-1].startswith("Successfully"):
                line = lines.pop()
                target_commands[target_name].append(line)

            continue

    return (target_map, target_commands, target_sorted, target_path)

if __name__ == "__main__":
    lines = []
    for line in fileinput.input():
        lines.append(line)
    lines.reverse()

    (target_map, target_commands, target_sorted, target_path) = from_lines(lines)

    target_sorted.reverse()

    # loop through targets and output rule and build information
    output = []
    for target_name in target_sorted:
        target_base = target_name.replace("/", "_")
        target_base = target_base.replace(".", "_")

        commands = target_commands[target_name]
        if len(commands) == 0:
            continue

        command = " && ".join(commands)
        command = command.replace('\n', '')
        if 'Windows' == platform.system():
            if len(commands) > 1 or command.split(maxsplit=1)[0].upper() in cmd_builtins:
                command = 'cmd /c "' + command + '"'

        rule = "rule " + target_base + "_rule\n  command = " + command

        deps = target_map[target_name]
        dep_list = ""
        for dep in deps:
            if dep in target_path:
                dep_list += target_path[dep] + " "
            else:
                dep_list += dep + " "
        build = "build " + target_name + ": " + target_base + "_rule " + dep_list.replace(':', '$:')

        output.append(rule)
        output.append(build)

    print("\n".join(output))

