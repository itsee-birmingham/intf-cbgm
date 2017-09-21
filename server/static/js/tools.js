'use strict';

/**
 * This module implements helper functions and is a container for all stuiff
 * that doesn't fit elsewhere.
 *
 * @module tools
 * @author Marcello Perathoner
 */

define([], function () {
    /**
     * Format a string in python fashion.  "{count} items found"
     *
     * @function format
     *
     * @param {string} s  - The string to format
     * @param {dict} data - A dictionary of key: value
     *
     * @return {string} - The formatted string
     */

    function format(s, data) {
        return s.replace(/\{([_\w][_\w\d]*)\}/gm, function (match, p1) {
            return data[p1];
        });
    }

    /**
     * Transform a string so that numbers in the string sort naturally.
     *
     * Transform any contiguous run of digits so that it sorts
     * naturally during an alphabetical sort. Every run of digits gets
     * the length of the run prepended, eg. 123 => 3123, 123456 =>
     * 6123456.
     *
     * @param {string} s - The input string
     *
     * @return {string} - The transformed string
     */

    function natural_sort(s) {
        return s.replace(/\d+/g, function (match, dummy_offset, dummy_string) {
            return match.length + match;
        });
    }

    /**
     * Return a map of the query parameters in the url of this page.
     *
     * @function get_query_params
     *
     * @return {Oject} A map of parameter = value
     */

    function get_query_params() {
        var query = {};
        location.search.substr(1).split('&').forEach(function (item) {
            var s = item.split('=');
            query[s[0]] = s[1];
        });
        return query;
    }

    /**
     * Position a context menu aside an svg element.
     *
     * Since jQuery doesn't grok the SVG DOM, we have to calculate the
     * position of the menu manually.
     *
     * @param {Object} menu   - The menu
     * @param {Object} target - The DOM object to attach the menu to
     */

    function svg_contextmenu(menu, target) {
        $(target).closest('div.panel').append(menu);

        var rect = target.getBoundingClientRect();
        var bodyRect = document.body.getBoundingClientRect(); // account for scrolling
        var ev = new $.Event('click');
        ev.pageY = rect.top - bodyRect.top;
        ev.pageX = rect.right - bodyRect.left;
        menu.position({
            'my': 'left top',
            'collision': 'flipfit flip',
            'of': ev
        });
    }

    /**
     * Display an auto-closing alert window.
     *
     * @param {Object} xhr - The server response containing the
     *                          message.  The JSON response must
     *                          contain an Object with a message
     *                          field.
     * @param {jQuery} $panel - The panel to append the window to.
     */

    function xhr_alert(xhr, $panel) {
        if (!$panel) {
            $panel = $('body');
        }
        var category = 'danger';

        if (xhr.responseJSON) {
            var $alert = $('\n                <div class="alert alert-' + category + ' alert-dismissible alert-margins" role="alert">\n                    <button type="button" class="close" data-dismiss="alert"\n                            aria-label="Close"><span aria-hidden="true">&times;</span></button>\n                    ' + xhr.responseJSON.message + '\n                 </div>\n                ');
            $alert.appendTo($panel).hide();
            $alert.on('click', 'button[data-dismiss="alert"]', function () {
                $alert.stop(true, true).slideUp(function () {
                    $alert.remove();
                });
            });
            $alert.slideDown().delay(5000).slideUp();
        }
    }

    function init() {}

    return {
        'format': format,
        'natural_sort': natural_sort,
        'get_query_params': get_query_params,
        'init': init,
        'svg_contextmenu': svg_contextmenu,
        'xhr_alert': xhr_alert
    };
});

//# sourceMappingURL=tools.js.map