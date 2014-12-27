"""tablescroll.py -- High-level scroll management. This ensures that behavior
like scroll_to_item works the same way across platforms.
"""

from mvc.errors import WidgetActionError


class ScrollbarOwnerMixin(object):
    """Scrollbar management for TableView.
    
    External methods have undecorated names; internal methods start with _.

    External methods:
    - handle failure themselves (e.g. return None or retry later)
    - return basic data types (e.g. (x, y) tuples)
    - use "tree" coordinates
        
    Internal methods (intended to be used by ScrollbarOwnerMixin and the
    platform implementations):
    - raise WidgetActionError subclasses on failure
    - use Rect/Point structs
    - also use "tree" coordinates
    """
    def __init__(self, _work_around_17153=False):
        self.__work_around_17153 = _work_around_17153
        self._scroll_to_iter_callback = None
        self.create_signal('scroll-range-changed')

    def scroll_to_iter(self, iter_, manual=True, recenter=False):
        """Scroll the given item into view.
        
        manual: scroll even if we were not following the playing item
        recenter: scroll even if item is in top half of view
        """
        try:
            item = self._get_item_area(iter_)
            visible = self._get_visible_area()
            manually_scrolled = self._manually_scrolled
        except WidgetActionError:
            if self._scroll_to_iter_callback:
                # We just retried and failed. Do nothing; we will retry again
                # next time scrollable range changes.
                return
            # We just tried and failed; schedule a retry when the scrollable
            # range changes.
            self._scroll_to_iter_callback = self.connect('scroll-range-changed',
                    lambda *a: self.scroll_to_iter(iter_, manual, recenter))
            return
        # If the above succeeded, we know the iter's position; this means we can
        # set_scroll_position to that position. That may work now or be
        # postponed until later, but either way we're done with scroll_to_iter.
        if self._scroll_to_iter_callback:
            self.disconnect(self._scroll_to_iter_callback)
            self._scroll_to_iter_callback = None
        visible_bottom = visible.y + visible.height
        visible_middle = visible.y + visible.height // 2
        item_bottom = item.y + item.height
        item_middle = item.y + item.height // 2
        in_top = item_bottom >= visible.y and item.y <= visible_middle
        in_bottom = item_bottom >= visible_middle and item.y <= visible_bottom
        if self._should_scroll(
                manual, in_top, in_bottom, recenter, manually_scrolled):
            destination = item_middle - visible.height // 2
            self._set_vertical_scroll(destination)
            # set_scroll_position will take care of scroll to the position when
            # possible; this may or may not be now, but our work here is done.

    def set_scroll_position(self, position, restore_only=False,
            _hack_for_17153=False):
        """Scroll the top left corner to the given (x, y) offset from the origin
        of the view.

        restore_only: set the value only if no other value has been set yet
        """
        if _hack_for_17153 and not self.__work_around_17153:
            return
        if not restore_only or not self._position_set:
            self._set_scroll_position(position)

    @classmethod
    def _should_scroll(cls,
            manual, in_top, in_bottom, recenter, manually_scrolled):
        if not manual and manually_scrolled:
            # The user has moved the scrollbars since we last autoscrolled, and
            # we're deciding whether we should resume autoscrolling.
            # We want to do that when the currently-playing item catches up to
            # the center of the screen i.e. is part above the center, part below
            return in_top and in_bottom
        # This is a manual scroll, or we're already autoscrolling - so we no
        # longer need to worry about either manual or manually_scrolled
        if in_top:
            # The item is in the top half; let playback catch up with the
            # current scroll position, unless recentering has been requested
            return recenter
        if in_bottom:
            # We land here when:
            # - playback has begun with an item in the bottom half of the screen
            # - scroll is following sequential playback
            # Either way we want to jump down to the item.
            return True
        # We're scrolling to an item that's not in view because:
        # - playback has begun with an item that is out of sight
        # - we're autoscrolling on shuffle
        # Either way we want to show the item.
        return True

    def reset_scroll(self):
        """To scroll back to the origin; platform code might want to do
        something special to forget the current position when this happens.
        """
        self.set_scroll_position((0, 0))

    def get_scroll_position(self):
        """Returns the current scroll position, or None if not ready."""
        try:
            return tuple(self._get_scroll_position())
        except WidgetActionError:
            return None

    def _set_vertical_scroll(self, pos):
        """Helper to set our vertical position without affecting our horizontal
        position.
        """
        # FIXME: shouldn't reset horizontal position
        self.set_scroll_position((0, pos))
