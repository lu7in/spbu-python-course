import pytest
from project.task3.carrying import curry_explicit, uncurry_explicit


class TestCurryExplicit:
    """Tests for curry_explicit"""

    def test_negative_arity(self):
        """Error test for negative arity"""
        with pytest.raises(ValueError, match="Arity must be a positive integer"):
            curry_explicit(lambda x: x, -1)

    def test_zero_arity(self):
        """Zero arity test"""
        func = curry_explicit(lambda: 42, 0)
        assert func() == 42

    def test_single_argument(self):
        """curry test for single argument"""
        curried = curry_explicit(lambda x: x + 1, 1)
        assert curried(5) == 6

    def test_error_more_than_arguments(self):
        """curry test for multiple arguments"""
        curried = curry_explicit(lambda a, b, c: a + b + c, 3)
        with pytest.raises(
            TypeError,
            match="Curried function accepts only one positional argument per call",
        ):
            assert curried(1, 2)(3)
            assert curried(1, 2, 3)

    def test_too_many_arguments(self):
        """error test for too many arguments"""
        curried = curry_explicit(lambda x, y: x + y, 2)
        with pytest.raises(TypeError):
            curried(1)(2)(3)

    def test_curry_decorator_behavior(self):
        """Curry decorator behavior"""

        def add(a, b, c):
            return a + b + c

        add_curried = curry_explicit(add, 3)

        assert add_curried(1)(2)(3) == 6

    def test_var_arity_function(self):
        """Curried functions with variable arity test"""

        def var_sum(*args):
            return sum(args)

        curried_var = curry_explicit(var_sum, 3)
        with pytest.raises(
            TypeError,
            match="Curried function accepts only one positional argument per call",
        ):
            curried_var(1, 2)

        assert curried_var(1)(2)(3) == 6

    def test_builtin_function(self):
        """Curried built-in functions test"""
        curried_max = curry_explicit(max, 2)

        with pytest.raises(
            TypeError,
            match="Curried function accepts only one positional argument per call",
        ):
            curried_max(1, 2)

        assert curried_max(1)(2) == 2


class TestUncurryExplicit:
    """Tests for uncurry_explicit"""

    def test_negative_arity(self):
        """Error test for negative arity"""
        with pytest.raises(ValueError, match="Arity must be a positive integer"):
            uncurry_explicit(lambda x: x, -1)

    def test_zero_arity(self):
        """Zero arity test"""

        def func():
            return 42

        func = uncurry_explicit(func, 0)
        assert func() == 42

    def test_single_argument(self):
        """Uncary test for single argument"""
        uncurried = uncurry_explicit(lambda x: x + 1, 1)
        assert uncurried(5) == 6

    def test_multiple_arguments(self):
        """Uncary test for multiple arguments"""
        # Создаем каррированную функцию для теста
        curried = curry_explicit(lambda a, b, c: a + b + c, 3)
        uncurried = uncurry_explicit(curried, 3)
        assert uncurried(1, 2, 3) == 6

    def test_wrong_argument_count(self):
        """Error test for wrong arity"""
        uncurried = uncurry_explicit(lambda x: x, 1)
        with pytest.raises(ValueError, match="Expected 1 arguments, got 2"):
            uncurried(1, 2)

    def test_uncurry_identity(self):
        """Tests that uncurry(curry) is ID"""
        original = lambda a, b, c: a + b + c
        curried = curry_explicit(original, 3)
        uncurried = uncurry_explicit(curried, 3)
        assert uncurried(1, 2, 3) == original(1, 2, 3)

    def test_var_arity_function(self):
        """Uncurried functions with variable arity test"""

        def var_sum(*args):
            return sum(args)

        curried_var = curry_explicit(var_sum, 4)
        with pytest.raises(
            TypeError,
            match="Curried function accepts only one positional argument per call",
        ):
            curried_var(1, 2)
        assert curried_var(1)(2)(3)(4) == 10

    def test_builtin_function(self):
        """Uncurried built-in functions test"""
        curried_pow = curry_explicit(pow, 2)
        with pytest.raises(
            TypeError,
            match="Curried function accepts only one positional argument per call",
        ):
            curried_pow(2, 3)

        assert curried_pow(2)(3) == 8
