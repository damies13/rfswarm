window.isMenuOpen = false;

// Custom item renderer that handles alignment gutters and injects your custom icons cleanly
function patchSelectmenuRenderer($selectmenuWidget) {
    $selectmenuWidget.selectmenu("instance")._renderItem = function(ul, item) {
        var li = $("<li>"),
            wrapper = $("<div>", { text: item.label });

        if (item.disabled) {
            li.addClass("ui-state-disabled");
        }

        // Check if ANY option inside this specific menu container carries an icon class attribute
        var parentSelect = item.element.parent();
        var menuHasIcons = parentSelect.find("option[data-class]").length > 0;
        var currentIcon = item.element.attr("data-class");

        if (menuHasIcons) {
            if (currentIcon) {
                wrapper.addClass("menu-item-with-icon");
                $("<span>", { "class": "ui-icon " + currentIcon }).prependTo(wrapper);
            } else {
                wrapper.addClass("menu-item-spacer");
            }
        }

        // 🚀 Store the exact translation key directly onto the generated HTML list item 
        // so we can read it during click interactions safely
        if (item.element.attr("data-i18n")) {
            li.attr("data-action-key", item.element.attr("data-i18n"));
        }

        return li.append(wrapper).appendTo(ul);
    };
}

function loadMyUiPanels() {
    if (window.panelsLoaded) return;
    window.panelsLoaded = true;

    $("#menubar-pannel").empty().load("menu.html", function() {
        var $container = $(this);

        // Translate the newly loaded menu elements first
        $container.localize();

        var $selects = $container.find("select");

        // Initialize each dropdown menu element
        $selects.each(function() {
            var $this = $(this);
            
            // Keep a secure copy of your original translated header category name (e.g. "File", "Run")
            var originalMenuName = $this.find("option:first").text();

            // Generate the native selectmenu widget instance
            $this.selectmenu({
                classes: {
                    "ui-selectmenu-button": "ui-button"
                },
                open: function() {
                    window.isMenuOpen = true;
                },
                // 🌟 THE UNBREAKABLE REPEAT-CLICK FIX: 
                // Because the menu ALWAYS closes after an option interaction, forcing the text node 
                // inside the close callback guarantees it will freeze perfectly on every single click.
                close: function() {
                    var $button = $(this).selectmenu("instance").button;
                    $button.find(".ui-selectmenu-text").text(originalMenuName);
                }
            });

            // Apply our custom icon and alignment renderer patch to this instance
            patchSelectmenuRenderer($this);
            
            // Force the widget list wrapper container to re-render using our configurations
            $this.selectmenu("refresh");

            // Explicitly force the text node on startup to align with the translation dictionary
            $this.selectmenu("instance").button.find(".ui-selectmenu-text").text(originalMenuName);

            // Listen for clicks on the generated list items directly
            var menuMenuId = $this.selectmenu("instance").menuId;
            $("#" + menuMenuId).on("click", ".ui-menu-item", function(e) {
                var actionKey = $(this).attr("data-action-key");
                if (actionKey) {
                    console.log("Executed menu item action:", actionKey);
                }
                
                $this.selectmenu("close");
                window.isMenuOpen = false;
            });
        });



        // 🌟 HOVER MENU FLIPPING: Smoothly glide between sibling dropdown menus
        $container.find(".ui-selectmenu-button").on("mouseenter", function() {
            if (window.isMenuOpen) {
                var buttonId = $(this).attr("id");
                if (!buttonId) return;

                // Close all open selectmenus
                $selects.selectmenu("close");

                // Open the newly targeted column smoothly
                var selectId = buttonId.replace("-button", "");
                $("#" + selectId).selectmenu("open");
            }
        });

        // Group everything into the unified visual toolbar controlgroup layout last
        $container.find(".toolbar").controlgroup();
    });

    // Load the secondary toolbar template panel
    $("#toolbar-pannel").empty().load("toolbar.html", function() { 
        $(this).localize(); 
    });
    
    $('body').localize();
}

// GLOBAL CLICK-AWAY CLOSE MONITOR
$(document).on("click", function(event) {
    var $target = $(event.target);
    if (!$target.closest("#menubar-pannel").length) {
        window.isMenuOpen = false;
    } else if ($target.closest(".ui-selectmenu-button").length) {
        setTimeout(function() {
            var activePopups = $(".ui-selectmenu-menu").filter(":visible");
            window.isMenuOpen = activePopups.length > 0;
        }, 50);
    }
});

// Core Translation Initialization Core Gateway Listener
$(function() {
    if (typeof i18next !== 'undefined' && i18next.isInitialized) {
        loadMyUiPanels();
    } else if (typeof i18next !== 'undefined') {
        $(document).one('i18n:complete', function() {
            loadMyUiPanels();
        });
        i18next.one('initialized', function() {
            loadMyUiPanels();
        });
    }
});
