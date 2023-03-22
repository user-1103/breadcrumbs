"""
The Lexer class used for this tool.
"""

import re

from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.lexer import RegexLexer, bygroups, default, include
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Generic, Literal, Punctuation
from pygments.util import ClassNotFound

class TodotxtLexer(RegexLexer):
    """
    Lexer for Todo.txt todo list format.
    .. versionadded:: 2.0
    """

    name = 'Todotxt'
    url = 'http://todotxt.com/'
    aliases = ['todotxt']
    # *.todotxt is not a standard extension for Todo.txt files; including it
    # makes testing easier, and also makes autodetecting file type easier.
    filenames = ['todo.txt', '*.todotxt']
    mimetypes = ['text/x-todo']

    # Aliases mapping standard token types of Todo.txt format concepts
    CompleteTaskText = Operator  # Chosen to de-emphasize complete tasks
    IncompleteTaskText = Text    # Incomplete tasks should look like plain text

    # Priority should have most emphasis to indicate importance of tasks
    Priority = Generic.Heading
    # Dates should have next most emphasis because time is important
    Date = Generic.Subheading

    # Project and context should have equal weight, and be in different colors
    Project = Generic.Error
    Context = String
    Tag = Generic.Traceback

    # If tag functionality is added, it should have the same weight as Project
    # and Context, and a different color. Generic.Traceback would work well.

    # Regex patterns for building up rules; dates, priorities, projects, and
    # contexts are all atomic
    # TODO: Make date regex more ISO 8601 compliant
    date_regex = r'\d{4,}-\d{2}-\d{2}'
    priority_regex = r'\([A-Z]\)'
    project_regex = r'\+\S+'
    context_regex = r'@\S+'
    tag_regex = r"\w*:\w*"

    # Compound regex expressions
    complete_one_date_regex = r'(x )(' + date_regex + r')'
    complete_two_date_regex = (complete_one_date_regex + r'( )(' +
                               date_regex + r')')
    priority_date_regex = r'(' + priority_regex + r')( )(' + date_regex + r')'

    tokens = {
        # Should parse starting at beginning of line; each line is a task
        'root': [
            # Complete task entry points: two total:
            # 1. Complete task with two dates
            (complete_two_date_regex, bygroups(CompleteTaskText, Date,
                                               CompleteTaskText, Date),
             'complete'),
            # 2. Complete task with one date
            (complete_one_date_regex, bygroups(CompleteTaskText, Date),
             'complete'),

            # Incomplete task entry points: six total:
            # 1. Priority plus date
            (priority_date_regex, bygroups(Priority, IncompleteTaskText, Date),
             'incomplete'),
            # 2. Priority only
            (priority_regex, Priority, 'incomplete'),
            # 3. Leading date
            (date_regex, Date, 'incomplete'),
            # 4. Leading context
            (context_regex, Context, 'incomplete'),
            # 5. Leading project
            (project_regex, Project, 'incomplete'),
            # 5.5. Leading project
            (tag_regex, Tag, 'incomplete'),
            # 6. Non-whitespace catch-all
            (r'\S+', IncompleteTaskText, 'incomplete'),
        ],

        # Parse a complete task
        'complete': [
            # Newline indicates end of task, should return to root
            (r'\s*\n', CompleteTaskText, '#pop'),
            # Tokenize contexts and projects
            (context_regex, Context),
            (project_regex, Project),
            (tag_regex, Tag),
            # Tokenize non-whitespace text
            (r'\S+', CompleteTaskText),
            # Tokenize whitespace not containing a newline
            (r'\s+', CompleteTaskText),
        ],

        # Parse an incomplete task
        'incomplete': [
            # Newline indicates end of task, should return to root
            (r'\s*\n', IncompleteTaskText, '#pop'),
            # Tokenize contexts and projects
            (context_regex, Context),
            (project_regex, Project),
            (tag_regex, Tag),
            # Tokenize non-whitespace text
            (r'\S+', IncompleteTaskText),
            # Tokenize whitespace not containing a newline
            (r'\s+', IncompleteTaskText),
        ],
    }
