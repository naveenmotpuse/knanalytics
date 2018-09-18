/*  jQuery Nice Select - v1.1.0
    https://github.com/hernansartorio/jquery-nice-select
    Made by HernÃ¡n Sartorio  */

(function($) {

  $.fn.niceSelect = function(method) {
     //Anu 30-march-2017 
      var lastTxt = "";

    // Methods
    if (typeof method == 'string') {
      if (method == 'update') {
        this.each(function() {
          var $select = $(this);
          var $dropdown = $(this).next('.nice-select');
          var open = $dropdown.hasClass('open');

          if ($dropdown.length) {
            $dropdown.remove();
            create_nice_select($select);

            if (open) {
              $select.next().trigger('click');
            }
          }
        });
      } else if (method == 'destroy') {
        this.each(function() {
          var $select = $(this);
          var $dropdown = $(this).next('.nice-select');

          if ($dropdown.length) {
            $dropdown.remove();
            $select.css('display', '');
          }
        });
        if ($('.nice-select').length == 0) {
          $(document).off('.nice_select');
        }
      } else {
        console.log('Method "' + method + '" does not exist.')
      }
      return this;
    }

    // Hide native select
    this.hide();

    // Create custom markup
    this.each(function() {
      var $select = $(this);

      if (!$select.next().hasClass('nice-select')) {
        create_nice_select($select);
      }
    });

    function create_nice_select($select) {

      $select.after($('<div></div>')
        .addClass('nice-select')
        .addClass($select.attr('class') || '')
        .addClass($select.attr('disabled') ? 'disabled' : '')
        .attr('tabindex', $select.attr("tabindex"))
        .attr('style', $select.attr("style").replace("display: none;",""))
        .html('<div class="current"></div><ul class="list"></ul>')
      );

      var $dropdown = $select.next();
      var $options = $select.find('option');
      var $selected = $select.find('option:selected');


      $dropdown.find('.current').html($selected.data('display') || $selected.text());
	  	if($select.val() != "" && $select.val() != "All"  ){
			$dropdown.addClass("ddSelected");
			$dropdown.find('.current').addClass("ddtxt");
	  	}
        //Anu 30-march-2017 search within list
        if ($options.length > 5) {
            $dropdown.append('<div class="searchWithinList"><input class="searchtextlst" name="searchtext" id="searchtext" type="text" placeholder="search here..."/></div>');
            $dropdown.find('ul').css("margin-top", "37px");
        }

      $options.each(function(i) {
        var $option = $(this);
        var display = $option.data('display');

        $dropdown.find('ul').append($('<li></li>')
          .attr('data-value', $option.val())
          .attr('data-display', (display || null))
          .addClass('option' +
            ($option.is(':selected') ? ' selected' : '') +
            ($option.is(':disabled') ? ' disabled' : ''))
          .html($option.text())
        );
      });
    }

    /* Event listeners */

    // Unbind existing events in case that the plugin has been initialized before
    $(document).off('.nice_select');

    // Open/close
    $(document).on('click.nice_select', '.nice-select', function (event) {

        //Anu 30-march-2017 search within list
        if (event.target.name == "searchtext") {
            return;
        }

        var $dropdown = $(this);

        $('.nice-select.open').find(".searchWithinList").hide();
        $('.nice-select').not($dropdown).removeClass('open');
        $dropdown.toggleClass('open');

        //Anu 30-march-2017 clear search within list
        if ($dropdown.hasClass('open')) {
            $dropdown.find('.option');
            $dropdown.find('.focus').removeClass('focus');
            $dropdown.find('.selected').addClass('focus');
            
            var _ul = $dropdown.find("ul");
            var _stxt = $dropdown.find(".searchtextlst");
            if (_stxt.val() != undefined && _stxt.val().trim() != "") {
                _ul.find("li").show();
            }
            _stxt.val("");
            var _stxtbox = $dropdown.find(".searchWithinList").css({ "display": "block", "width": (_ul.width() - 1) + "px" });
           // _ul.css("margin-top", (_stxtbox.height() - 10) + "px");
        } else {
            $dropdown.focus();

            $dropdown.find(".searchWithinList").hide()
            $dropdown.find(".searchtextlst").value = "";
        }
    });

    // Close when clicking outside
    $(document).on('click.nice_select', function (event) {
        if ($(event.target).closest('.nice-select').length === 0) {
            $('.nice-select.open').find(".searchWithinList").hide();
        $('.nice-select').removeClass('open').find('.option');
      }
    });

    // Option click
    $(document).on('click.nice_select', '.nice-select .option:not(.disabled)', function (event) {
        //debugger;
      var $option = $(this);
      var $dropdown = $option.closest('.nice-select');

      $dropdown.find('.selected').removeClass('selected');
      $option.addClass('selected');

      var text = $option.data('display') || $option.html();
      $dropdown.find('.current').html(text);

      $dropdown.prev('select').val($option.data('value')).trigger('change');
      //Anu 17-feb-2017 add custom style with class
      if ($option.data('value') != "" && $option.data('value') != "All") {
          $dropdown.addClass("ddSelected"); 
          $dropdown.find('.current').addClass("ddtxt");
      }
      else {
          $dropdown.removeClass("ddSelected");
          $dropdown.find('.current').removeClass("ddtxt");
      }
    });

    $(document).on('keyup.nice_select', '.nice-select', function (event) {
        if (event.target.id != "searchtext") {
            return;
        }
        var stxt = event.target.value.toLowerCase();
        stxt = stxt.trim();
        if (lastTxt == stxt) {
            return;
        }
        lastTxt = stxt;
        //console.log(stxt);
        var _ul = $(event.target).parents(".nice-select").find("ul");
        var lst = _ul.find("li.option");
        if (stxt != "") {
            for (var i = 0; i < lst.length; i++) {
                if ((lst[i].attributes["data-value"].value != "" && lst[i].attributes["data-value"].value != "-1") && (lst[i].innerText.toLowerCase() + "").indexOf(stxt) == -1) {
                    lst[i].style.display = "none";
                }
                else {
                    lst[i].style.display = "";
                }
            }
        }
        else {
            $(lst).show();
        }

        var _hgt = $(event.target).parent().css("width", (_ul.width() - 1) + "px").height();
        _hgt = Math.round(_hgt);
       // _ul.css("margin-top", (_hgt - 10) + "px");
        return;
    });

    //Keyboard events
    $(document).on('keydown.nice_select', '.nice-select', function (event) {
        if (event.target.id == "searchtext") {
            return;
        }
      var $dropdown = $(this);
      var $focused_option = $($dropdown.find('.focus') || $dropdown.find('.list .option.selected'));

      // Space or Enter
      if (event.keyCode == 32 || event.keyCode == 13) {
        if ($dropdown.hasClass('open')) {
          $focused_option.trigger('click');
        } else {
          $dropdown.trigger('click');
        }
        return false;
      // Down
      } else if (event.keyCode == 40) {
        if (!$dropdown.hasClass('open')) {
          $dropdown.trigger('click');
        } else {
          var $next = $focused_option.nextAll('.option:not(.disabled)').first();
          if ($next.length > 0) {
            $dropdown.find('.focus').removeClass('focus');
            $next.addClass('focus');
          }
        }
        return false;
      // Up
      } else if (event.keyCode == 38) {
        if (!$dropdown.hasClass('open')) {
          $dropdown.trigger('click');
        } else {
          var $prev = $focused_option.prevAll('.option:not(.disabled)').first();
          if ($prev.length > 0) {
            $dropdown.find('.focus').removeClass('focus');
            $prev.addClass('focus');
          }
        }
        return false;
      // Esc
      } else if (event.keyCode == 27) {
        if ($dropdown.hasClass('open')) {
          $dropdown.trigger('click');
        }
      // Tab
      } else if (event.keyCode == 9) {
        if ($dropdown.hasClass('open')) {
          return false;
        }
      }
    });

    // Detect CSS pointer-events support, for IE <= 10. From Modernizr.
    var style = document.createElement('a').style;
    style.cssText = 'pointer-events:auto';
    if (style.pointerEvents !== 'auto') {
      $('html').addClass('no-csspointerevents');
    }

    return this;

  };

}(jQuery));