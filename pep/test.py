"""
Test that our implementation of PEP 750, which is currently partially in the
fork of cpython, and partially in the __init__.py in this repository, works.

See the __init__.py for a more detailed explanation.
"""

import asyncio
from string.templatelib import Interpolation, Template

import pytest


def test_empty():
    template = t""
    assert isinstance(template, Template)
    assert template.strings == (
        "",
    )  # This will fail if interleaving is not implemented
    assert template.interpolations == ()
    assert list(template) == []


def test_simple():
    template = t"hello"
    assert isinstance(template, Template)
    assert template.strings == ("hello",)
    assert template.interpolations == ()
    assert list(template) == ["hello"]


def test_only_interpolation():
    template = t"{42}"
    assert isinstance(template, Template)
    assert template.strings == ("", "")
    assert template.interpolations[0].value == 42
    assert list(template)[0].value == 42


def test_mixed():
    v = 99
    template = t"hello{42}world{v}goodbye"
    assert isinstance(template, Template)
    assert template.strings == ("hello", "world", "goodbye")
    assert template.interpolations[0].value == 42
    assert template.interpolations[1].value == v
    assert list(template)[1].value == 42
    assert list(template)[3].value == v


def test_conversion():
    template = t"{42!a}"
    assert isinstance(template, Template)
    assert template.interpolations[0].value == 42
    assert template.interpolations[0].conversion == "a"


def test_format_spec():
    template = t"{42:04d}"
    assert isinstance(template, Template)
    assert template.interpolations[0].value == 42
    assert template.interpolations[0].format_spec == "04d"


def test_format_spec_and_conversion():
    template = t"{42!r:04d}"
    assert isinstance(template, Template)
    assert template.interpolations[0].value == 42
    assert template.interpolations[0].conversion == "r"
    assert template.interpolations[0].format_spec == "04d"


def test_format_spec_with_interpolation():
    value = 42
    precision = 2
    template = t"Value: {value:.{precision}f}"
    assert isinstance(template, Template)
    assert template.interpolations[0].value == 42
    assert template.interpolations[0].format_spec == ".2f"


def test_add_template_str():
    template = t"hello" + "world"
    assert isinstance(template, Template)
    assert template.strings == ("helloworld",)
    assert template.interpolations == ()
    assert list(template) == ["helloworld"]


def test_add_template_str_2():
    name = "world"
    template = t"hello {name}!" + " how are you?"
    assert isinstance(template, Template)
    assert template.strings == ("hello ", "!" + " how are you?")
    assert template.interpolations[0].value == name
    contents = list(template)
    assert len(contents) == 3
    assert contents[1].value == name


def test_add_template_template():
    template = t"hello" + t"world"
    assert isinstance(template, Template)
    assert template.strings == ("helloworld",)
    assert template.interpolations == ()
    assert list(template) == ["helloworld"]


def test_add_template_template_2():
    name = "world"
    other = "you"
    template = t"hello {name}!" + t" how are {other}?"
    assert isinstance(template, Template)
    assert template.strings == ("hello ", "!" + " how are ", "?")
    assert len(template.interpolations) == 2
    assert template.interpolations[0].value == name
    assert template.interpolations[1].value == other
    contents = list(template)
    assert len(contents) == 5
    assert contents[1].value == name
    assert contents[3].value == other


def test_add_str_template():
    template = "hello" + t"world"
    assert isinstance(template, Template)
    assert template.strings == ("helloworld",)
    assert template.interpolations == ()
    assert list(template) == ["helloworld"]


def test_add_str_template_2():
    name = "world"
    template = "hello " + t"there, {name}!"
    assert isinstance(template, Template)
    assert template.strings == ("hello " + "there, ", "!")
    assert len(template.interpolations) == 1
    assert template.interpolations[0].value == name
    contents = list(template)
    assert len(contents) == 3
    assert contents[1].value == name


def test_interpolation_constructor_1():
    i1 = Interpolation(42, "i1")
    assert i1.value == 42
    assert i1.expression == "i1"
    assert i1.conversion is None
    assert i1.format_spec == ""


def test_interpolation_constructor_2():
    i1 = Interpolation(42, "i1", "a")
    assert i1.value == 42
    assert i1.expression == "i1"
    assert i1.conversion == "a"
    assert i1.format_spec == ""


def test_interpolation_constructor_3():
    i1 = Interpolation(42, "i1", "a", ",.2f")
    assert i1.value == 42
    assert i1.expression == "i1"
    assert i1.conversion == "a"
    assert i1.format_spec == ",.2f"


def test_interpolation_constructor_kwargs_1():
    i1 = Interpolation(value=42, expression="i1")
    assert i1.value == 42
    assert i1.expression == "i1"
    assert i1.conversion is None
    assert i1.format_spec == ""


def test_interpolation_constructor_kwargs_2():
    """Test the Interpolation constructor with various valid arguments."""
    i1 = Interpolation(value=42, expression="i1", conversion="a")
    assert i1.value == 42
    assert i1.expression == "i1"
    assert i1.conversion == "a"
    assert i1.format_spec == ""


def test_interpolation_constructor_kwargs_3():
    """Test the Interpolation constructor with various valid arguments."""
    i1 = Interpolation(value=42, expression="i1", format_spec=",.2f")
    assert i1.value == 42
    assert i1.expression == "i1"
    assert i1.conversion == None
    assert i1.format_spec == ",.2f"


def test_interpolation_constructor_kwargs_4():
    """Test the Interpolation constructor with various valid arguments."""
    i1 = Interpolation(value=42, expression="i1", conversion="a", format_spec=",.2f")
    assert i1.value == 42
    assert i1.expression == "i1"
    assert i1.conversion == "a"
    assert i1.format_spec == ",.2f"


def test_interpolation_constructor_invalid_1():
    with pytest.raises(TypeError):
        _ = Interpolation(42)


def test_interpolation_constructor_invalid_2():
    with pytest.raises(TypeError):
        # expr must be a string
        _ = Interpolation(42, None)


def test_interpolation_constructor_invalid_3():
    with pytest.raises(ValueError):
        # conv must be one of 'a', 'r', 's' or None
        _ = Interpolation(42, "i1", "bogus")


def test_interpolation_constructor_invalid_kwargs_1():
    with pytest.raises(TypeError):
        # No such kwarg
        _ = Interpolation(whatever=42)


def test_template_constructor_invalid():
    # Only str and Interpolation objects are allowed in the constructor
    with pytest.raises(TypeError):
        _ = Template(42)


def test_template_constructor_interleaving_empty():
    # PEP 750 requires that `Template.args` contains one more string than
    # interpolations. If there are no interpolations, we must therefore have
    # one empty string. `Template.args` can never be empty.
    template = Template()
    assert template.strings == ("",)


def test_template_constructor_interleaving_single_string():
    template = Template("hello")
    assert template.strings == ("hello",)


def test_template_constructor_interleaving_neighboring_strings():
    template = Template("hello", "world")
    assert template.strings == ("helloworld",)


def test_template_constructor_interleaving_single_interpolation():
    i1 = Interpolation(42, "i1", None, "")
    template = Template(i1)
    assert template.strings == ("", "")
    assert template.interpolations == (i1,)


def test_template_constructor_interleaving_neighboring_interpolations():
    i1 = Interpolation(42, "i1", None, "")
    i2 = Interpolation(99, "i2", None, "")
    template = Template(i1, i2)
    assert template.strings == ("", "", "")
    assert template.interpolations == (i1, i2)


def test_template_constructor_interleaving_all_the_things():
    i1 = Interpolation(42, "i1", None, "")
    i2 = Interpolation(99, "i2", None, "")
    i3 = Interpolation(100, "i3", None, "")
    i4 = Interpolation(101, "i4", None, "")
    template = Template("hello", "there", i1, i2, "wow", "neat", i3, "fun", i4)
    assert template.strings == (
        "hellothere",
        "",
        "wowneat",
        "fun",
        "",
    )
    assert template.interpolations == (i1, i2, i3, i4)


def test_implicit_concat_str_template():
    template = "hello" t"world"
    assert isinstance(template, Template)
    assert template.strings == ("helloworld",)
    assert len(template.interpolations) == 0


def test_implicit_concat_template_str():
    template = t"hello" "world"
    assert isinstance(template, Template)
    assert template.strings == ("helloworld",)
    assert len(template.interpolations) == 0


def test_implicit_concat_fstr_template():
    name = "world"
    template = f"hello {name}, " t"your name is {name}!"
    assert isinstance(template, Template)
    assert template.strings == ("hello world, your name is ", "!")
    assert len(template.interpolations) == 1
    assert template.interpolations[0].value == name


def test_implicit_concat_template_fstr():
    name = "world"
    template = t"hello {name}, " f"your name is {name}!"
    assert isinstance(template, Template)
    assert template.strings == ("hello ", ", your name is world!")
    assert len(template.interpolations) == 1
    assert template.interpolations[0].value == name


def test_template_debug_specifier():
    name = "World"
    template = t"Hello {name=}"
    assert template.strings[0] == "Hello name="
    assert template.interpolations[0].value == "World"
    assert template.interpolations[0].conversion == "r"


def test_template_debug_specifier_expr_preserves_whitespace():
    name = "World"
    template = t"Hello {   name  = }"
    assert template.strings[0] == "Hello    name  = "
    assert template.interpolations[0].value == "World"
    assert template.interpolations[0].conversion == "r"


def test_template_debug_specifier_with_format_spec():
    value = 42
    template = t"Value: {value=:spec}"
    assert template.strings[0] == "Value: value="
    assert template.interpolations[0].value == 42
    assert template.interpolations[0].conversion == None
    assert template.interpolations[0].format_spec == "spec"


def test_template_raw_template_strings_1():
    trade = "shrubberies"
    template = rt'Did you say "{trade}"?\n'
    assert template.strings == (r'Did you say "', r'"?\n')
    assert len(template.interpolations) == 1
    assert template.interpolations[0].value == trade


def test_syntax_error_1():
    with pytest.raises(
        SyntaxError, match="t-string: valid expression required before '}'"
    ):
        # Use exec to avoid syntax error in the test itself
        exec('t"hello {}"')
        # Now, we got "f-string: valid expression required before '}'"


def test_nested_interpolation():
    """Test nested interpolations with correct interleaving"""
    name = "World"
    greeting = "Hello"
    template = t"{greeting} {t'{name}'}"
    assert isinstance(template, Template)
    assert template.strings == ("", " ", "")
    assert len(template.interpolations) == 2
    assert template.interpolations[0].value == greeting
    assert isinstance(template.interpolations[1].value, Template)


def test_multiple_adjacent_interpolations():
    """Test multiple adjacent interpolations with correct interleaving"""
    x, y = 10, 20
    template = t"{x}{y}{x + y}"
    assert isinstance(template, Template)
    assert template.strings == ("", "", "", "")
    assert len(template.interpolations) == 3
    assert template.interpolations[0].value == 10
    assert template.interpolations[1].value == 20
    assert template.interpolations[2].value == 30


def test_format_spec_with_interpolation():
    """Test format specifications with nested interpolations"""
    width = 10
    value = 42
    template = t"{value:.{width}f}"
    assert isinstance(template, Template)
    contents = list(template)
    assert len(contents) == 1
    assert contents[0].value == 42
    assert contents[0].format_spec == ".10f"


def test_complex_expressions_with_interleaving():
    """Test complex expressions maintaining interleaving"""
    x, y = 10, 20
    template = t"Result: {x * y} and {sum([1, 2, 3])}"
    assert isinstance(template, Template)
    assert template.strings == ("Result: ", " and ", "")
    assert len(template.interpolations) == 2
    assert template.interpolations[0].value == 200
    assert template.interpolations[1].value == 6


def test_unicode_with_interleaving():
    """Test Unicode strings with correct interleaving"""
    name = "世界"
    template = t"こんにちは{name}さん👋"
    assert isinstance(template, Template)
    assert template.strings == ("こんにちは", "さん👋")
    assert len(template.interpolations) == 1
    assert template.interpolations[0].value == name


def test_raw_template_with_interleaving():
    """Test raw template strings maintain correct interleaving"""
    path = r"C:\Users"
    template = rt"{path}\n\t"
    assert isinstance(template, Template)
    assert template.strings == (r"", r"\n\t")
    assert len(template.interpolations) == 1
    assert template.interpolations[0].value == path


def test_empty_template_with_whitespace():
    """Test template with only whitespace maintains correct interleaving"""
    template = t"   "
    assert isinstance(template, Template)
    assert template.strings == ("   ",)
    assert len(template.interpolations) == 0


def test_template_constructor_with_only_interpolations():
    """Test Template constructor with only interpolations"""
    x = Interpolation(1, "1")
    y = Interpolation(2, "2")
    template = Template(x, y)
    assert template.strings == ("", "", "")
    assert len(template.interpolations) == 2
    assert template.interpolations[0] is x
    assert template.interpolations[1] is y


def test_template_constructor_with_only_strings():
    """Test Template constructor with only strings"""
    template = Template("Hello", " ", "World")
    assert template.strings == ("Hello World",)
    assert len(template.interpolations) == 0


@pytest.mark.asyncio
async def test_await_in_interpolation():
    """Test that await is allowed in interpolations"""

    async def get_value():
        await asyncio.sleep(0.01)
        return 42

    template = t"Value: {await get_value()}"
    assert template.interpolations[0].value == 42


def test_template_multiline_string_whitespace():
    """Test whitespace handling in multiline template strings"""
    value = 42
    template = t"""
        First line
        {value}
            Indented line
    """
    assert isinstance(template, Template)
    assert template.strings[0].startswith("\n")
    assert "    Indented line" in template.strings[1]


def test_template_with_expressions_up_to_16():
    """Test templates with up to 16 expressions, which is known to work."""

    def build_template(n, extra=""):
        return "t'" + ("{x} " * n) + extra + "'"

    x = "X"
    # Test up to 16 expressions (known working limit)
    for i in range(1, 16):
        template = eval(build_template(i))
        assert isinstance(template, Template)
        assert len(template.strings) == i + 1
        assert len(template.interpolations) == i


def test_template_with_many_expressions_direct():
    working = t"{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}{12}{13}{14}{15}{16}{17}{18}{19}{20}{21}{22}{23}{24}{25}{26}{27}{28}{29}{30}"
    assert isinstance(working, Template)
    # This next line currently raises a TypeError exception:
    # TypeError: sequence item 0: expected str instance, templatelib.Interpolation found
    busted = t"{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}{11}{12}{13}{14}{15}{16}{17}{18}{19}{20}{21}{22}{23}{24}{25}{26}{27}{28}{29}{30}{31}"
    assert isinstance(busted, Template)


def test_template_with_many_expressions():
    """Test templates with more than 16 expressions.
    Current implementation raises MemoryError for more than 16 expressions."""

    def build_template(n, extra=""):
        return "t'" + ("{x} " * n) + extra + "'"

    x = "X"
    # Test well beyond 16 expressions
    for i in range(250, 260):
        template = eval(build_template(i))
        assert isinstance(template, Template)
        assert len(template.strings) == i + 1
        assert len(template.interpolations) == i
