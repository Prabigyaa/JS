"""
Tests for variable naming convention detection
"""

import unittest

from src.nlpserver.variable_conventions import VariableConventions, get_convention # noqa: E402


class TestVariableConventions(unittest.TestCase):

    def test_camel_case_only(self):
        """Test for cames case variables detection"""
        camel_case_variables = ["startServer", "loopEnd", "createConnection"]

        for variable in camel_case_variables:
            output_convention = get_convention(variable)
            self.assertEqual(len(output_convention), 1)
            self.assertEqual(output_convention[0], VariableConventions.Camelcase)

    def test_pascal_case_only(self):
        "Test for pascal case variables detection"
        pascal_case_variables = ["StartServer", "LoopEnd", "CreateConnection"]

        for variable in pascal_case_variables:
            output_convention = get_convention(variable)
            self.assertEqual(len(output_convention), 1)
            self.assertEqual(output_convention[0], VariableConventions.Pascalcase)

    def test_snake_case_only(self):
        "Test for snake case variables detection"
        snake_case_variables = ["start_server", "loop_end", "create_connection"]

        for variable in snake_case_variables:
            output_convention = get_convention(variable)
            self.assertEqual(len(output_convention), 1)
            self.assertEqual(output_convention[0], VariableConventions.Snakecase)

    def test_screaming_snake_case_only(self):
        "Test for screaming snake case variables detection"
        screaming_snake_case_variables = ["START_SERVER", "LOOP_END", "CREATE_CONNECTION"]

        for variable in screaming_snake_case_variables:
            output_convention = get_convention(variable)
            self.assertEqual(len(output_convention), 1)
            self.assertEqual(output_convention[0], VariableConventions.Screamingsnakecase)

    def test_mixes_cases(self):
        "Test for screaming snake case variables detection"

        # these requires requires for elements
        snake_and_camel = ["start_Server",]
        snake_and_pascal = ["Loop_End", ]
        pascal = ["STartThis", ]  # modified versions of pascal
        screaming_snake = ["CREATECONNECTION"]  # modified version of screaming_snake case, usually for constants

        for var1 in snake_and_camel:
            output1 = get_convention(var1)
            self.assertEqual(len(output1), 2)
            self.assertTrue(VariableConventions.Snakecase in output1)
            self.assertTrue(VariableConventions.Camelcase in output1)

        for var2 in snake_and_pascal:
            output2 = get_convention(var2)
            self.assertEqual(len(output2), 2)
            self.assertTrue(VariableConventions.Snakecase in output2)
            self.assertTrue(VariableConventions.Pascalcase in output2)

        for var3 in pascal:
            output3 = get_convention(var3)
            self.assertEqual(len(output3), 1)
            self.assertTrue(VariableConventions.Pascalcase in output3)

        for var4 in screaming_snake:
            output4 = get_convention(var4)
            self.assertEqual(len(output4), 1)
            self.assertTrue(VariableConventions.Screamingsnakecase in output4)


if __name__ == "__main__":
    unittest.main()
