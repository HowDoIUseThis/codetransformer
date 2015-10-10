from io import StringIO
from textwrap import dedent
from types import CodeType

from ..pretty import a, walk_code


def test_a(capsys):
    text = dedent(
        """
        def inc(a):
            return a + 1
        """
    )
    expected = dedent(
        """\
        Module(
          body=[
            FunctionDef(
              name='inc',
              args=arguments(
                args=[
                  arg(
                    arg='a',
                    annotation=None,
                  ),
                ],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
              ),
              body=[
                Return(
                  value=BinOp(
                    left=Name(id=a, ctx=Load())
                    op=Add(),
                    right=Num(1)
                  ),
                ),
              ],
              decorator_list=[],
              returns=None,
            ),
          ],
        )
        """
    )

    a(text)
    printed, _ = capsys.readouterr()
    assert printed == expected

    file_ = StringIO()
    a(text, file=file_)
    assert capsys.readouterr() == ('', '')

    result = file_.getvalue()
    assert result == expected


def test_walk_code():
    module = dedent(
        """\
        def foo():
            def bar():
                def buzz():
                    pass
                def bazz():
                    pass
                return buzz
            return bar
        """
    )

    co = compile(module, '<test>', 'exec')

    foo = [c for c in co.co_consts if isinstance(c, CodeType)][0]
    bar = [c for c in foo.co_consts if isinstance(c, CodeType)][0]
    buzz = [c for c in bar.co_consts
            if isinstance(c, CodeType) and c.co_name == 'buzz'][0]
    bazz = [c for c in bar.co_consts
            if isinstance(c, CodeType) and c.co_name == 'bazz'][0]

    result = list(walk_code(co))
    expected = [
        ('<module>', co),
        ('<module>.foo', foo),
        ('<module>.foo.bar', bar),
        ('<module>.foo.bar.buzz', buzz),
        ('<module>.foo.bar.bazz', bazz),
    ]

    assert result == expected