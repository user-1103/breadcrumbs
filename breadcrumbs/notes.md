## Standards of the breadcrumbs system.

### The .loaf file.

In its simplest terms, a loaf is a collection of breadcrumbs (just crumbs for short).
A crumb is log entry about something in your life you think is worth logging,
nothing more, nothingness. The idea is that as one goes about their day they will log down
whatever is worthy to log, leaving behind the titular trail of breadcrumbs.

From a file format perspective, a .loaf is a superset of the todo.txt format.
In addition to the rules laid out by that spec, a loaf follows the following:

#### "Completed" means "Archived"

Because one is intended to log more than just todos in a loaf, the completed
syntax `(x)` and completed date will be more generally referred to as "Archived".
A crumb is to be archived if it is no longer correct, relevant, ect.

### Creation and Archive Dates are required.

This is to allow the breadcrumbs system to work its magic. If a crumb is found
without one of these it will be given the default date of `1989-04-15`.

### TIME and ATIME tags.

To allow for more magic, breadcrumbs expects a `TIME` tag to exist with the
format `hh-mm` to mark creation time. The same goes for `ATIME` and archive time.
The default of `06-28` will be used if a time is found missing.

### Date, time, span, and sequence formats.

- Dates are ISO `yyyy-mm-dd`.
- Time is 24hr `hh-mm`. (Yes this is non ISO, and it hurts me.)
- Date and time together are `yyyy-mm-dd-hh-mm` (Also non ISO)
- Spans are used to refer to a span of time and take the format
  `<descriptor>-<descriptor>` where:
  - `<descriptor>` can be:
    - `<int><m,h,d,w,y>` to represent a number of minutes, hours, days, weeks,
      Or years (typically in the past).
    - Or `~` to represent an unbounded interval.
    - Eg. `20d-1h` would specify "between 20 days in the past and 1 hour in the past."
- Sequences are used to define a recurring event. This looks like:
  `<base>-<descriptor>` where:
  - `<descriptor>` is as found in a span. This time will then be added to base
    to figure out when the next occurrence is. 
  - `<base>` is ether:
    - `a` for archive time.
    - `c` for creation time.
    - `n` for now.
    - A datetime (`yyyy-mm-dd-hh-mm`) for a fixed time.  

### lowercase all the time.

Not a hard and fast rule, but because breadcrumbs is typically case-sensitive,
It's advised to keep things lowercase unless you know you aren't going to fuck it
up. I know I will. It also helps keep the relaxed, stream of though style of
logging that this is built for.

### Space is the default delimiter!

This more important if you are a programmer building plugins, but it can be
good to keep in mind that ` ` is used as the delimiter between tokens (internally
also called atoms) in the breadcrumbs system. This flows from the todo.txt
standard (Eg. `example:tag` is a tag and `example: tag` is not).

If you need to use spaces, use hyphens! (or underscores)!

The complete standard for delimiters is as follows:

1. ` / ` Forward slash surrounded by spaces is used to divide collections of atoms.
2. ` ` Space is used to divide atoms.
3. `-` Hyphen is used to divide parts of atoms.
4. `/` Slash, no spaces, can be used as an alternate to the hyphen when needed.

### Links

Computers are a bunch of tubes so (in the near future) breadcrumbs intends to
support the use of those tubes. To link something, just use a tag: Eg.
`http://endless.horse/`. You can also use the `loaf` tag to link to another
loaf; The `l` tag to link to another (see the link command) for more details.
One can also link to a file on disk with the `f` tag.


## Flow of the breadcrumbs system.

### 1. Configuration is loaded.

Once `top_level.py` is executed, it will build the configuration that will be
used to edit the loaf.

It does this by calling the `collect_config()` method from the `config.py` module.
`collect_config()` does the following:

1. Calls `collect_plugins()` for the default plugins.
2. Looks for a `.breadbox` directory, making one if necessary via `ensure_breadbox()`.
3. Calls `collect_plugins()` for the `config.py` plugin found in the breadbox.

Once all plugins have been loaded, `top_level.py` will tweak the config as requested by command line arguments via `collect_cmdline()`.

### 2. Loaf is loaded.

Once the config is settled, a Loaf object from `loaf.py` will be initiated.
When loading the loaf file, it will be safely converted into proper `.loaf` format
via `kneed_loaf()`.

### 3. Parse breadcrumb command.

Whether it comes from the CLI or the REPL, `top_level.py` will use `parse()` to run the command.

`parse()` will follow these steps:

1. The PREMACRO hook will be called.
2. Any macros defined in the config will be expanded via `expand_macros()`.
3. The PRECMD hook will be called
4. The requested command will be found in the config via `find_cmd()`.
5. The found command will be run via `run_cmd()` and exceptions will be caught.
6. If an error occurs while running the command the CMDERR hook will be run.
   Otherwise, the CMDOK will be called.
7. The POSTCMD hook will be run.
8. The loaf will be saved via `save()` if the command was successful.

### 5. Display of output.

Most commands will display output through calls to `display()`. This should
follow the rules outlined in the display standards.

### 6. Exit.

On crash or user exit the `Mañana()` function will be called, respectively calling the hooks:

- EXIT
- SAFEEXIT
- FATALEXIT


