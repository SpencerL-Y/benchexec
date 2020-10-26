# This file is part of BenchExec, a framework for reliable benchmarking:
# https://github.com/sosy-lab/benchexec
#
# SPDX-FileCopyrightText: 2007-2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import benchexec.util as util
import benchexec.tools.template
import benchexec.result as result


class Tool(benchexec.tools.template.BaseTool2):
    """
    Wrapper for a Predator - Hunting Party
    http://www.fit.vutbr.cz/research/groups/verifit/tools/predator-hp/
    """

    REQUIRED_PATHS = ["predator", "predator-bfs", "predator-dfs", "predatorHP.py"]

    def executable(self, tool_locator):
        return tool_locator.find_executable("predatorHP.py")

    def name(self):
        return "PredatorHP"

    def version(self, executable):
        return self._version_from_tool(executable, use_stderr=True)

    def cmdline(self, executable, options, task, rlimits):
        spec = (
            ["--propertyfile", task.property_file]
            if task.property_file is not None
            else []
        )

        data_model_param = util.get_data_model_from_task(
            task,
            {"ILP32": "--compiler-options=-m32", "LP64": "--compiler-options=-m64"},
        )
        if data_model_param and data_model_param not in options:
            options += [data_model_param]

        return [executable] + options + spec + list(task.input_files_or_identifier)

    def determine_result(self, run):
        output = "\n".join(run.output)
        status = "UNKNOWN"
        if "UNKNOWN" in output:
            status = result.RESULT_UNKNOWN
        elif "TRUE" in output:
            status = result.RESULT_TRUE_PROP
        elif "FALSE(valid-memtrack)" in output:
            status = result.RESULT_FALSE_MEMTRACK
        elif "FALSE(valid-deref)" in output:
            status = result.RESULT_FALSE_DEREF
        elif "FALSE(valid-free)" in output:
            status = result.RESULT_FALSE_FREE
        elif "FALSE(valid-memcleanup)" in output:
            status = result.RESULT_FALSE_MEMCLEANUP
        elif "FALSE" in output:
            status = result.RESULT_FALSE_REACH
        if status == "UNKNOWN" and run.was_timeout:
            status = "TIMEOUT"
        return status
