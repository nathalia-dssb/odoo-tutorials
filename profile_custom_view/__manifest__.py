{
    "name": "Profile Custom View",
    "summary": "Profile custom view module.",
    "author": "Vauxoo",
    "license": "LGPL-3",
    "website": "https://www.vauxoo.com/",
    "category": "Customizations",
    "version": "19.0.1.0.0",
    "depends": ["portal"],
    'data': [
        'views/portal_views.xml',
    ],
    "assets": {
        "web._assets_frontend_helpers": [
            ("prepend", "profile_custom_view/static/src/scss/bootstrap_overridden.scss"),
        ],
        "web.assets_frontend": [
            "profile_custom_view/static/src/email_autocomplete/email_autocomplete.js",
            "profile_custom_view/static/src/email_autocomplete/email_autocomplete.xml",
        ],
    },
    "application": True,
}
