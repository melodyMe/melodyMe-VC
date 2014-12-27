"""Define keyboard input in a platform-independant way."""

(CTRL, ALT, SHIFT, CMD, MOD, RIGHT_ARROW, LEFT_ARROW, UP_ARROW,
 DOWN_ARROW, SPACE, ENTER, DELETE, BKSPACE, ESCAPE,
 F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12) = range(26)

class Shortcut:
    """Defines a shortcut key combination used to trigger this
    menu item.

    The first argument is the shortcut key.  Other arguments are
    modifiers.

    Examples:

    >>> Shortcut("x", MOD)
    >>> Shortcut(BKSPACE, MOD)

    This is wrong:

    >>> Shortcut(MOD, "x")
    """
    def __init__(self, shortcut, *modifiers):
        self.shortcut = shortcut
        self.modifiers = modifiers

    def _get_key_symbol(self, value):
        """Translate key values to their symbolic names."""
        if isinstance(self.shortcut, int):
            shortcut_string = '<Unknown>'
            for name, value in globals().iteritems():
                if value == self.shortcut:
                    return name
        return repr(value)

    def __str__(self):
        shortcut_string = self._get_key_symbol(self.shortcut)
        mod_string = repr(set(self._get_key_symbol(k) for k in
                              self.modifiers))
        return "Shortcut(%s, %s)" % (shortcut_string, mod_string)
