var Urls, exports;
exports = this;

exports.Urls = (function () {

    function Urls() {}

    Urls._instance = {
        url_patterns:{}
    };

    Urls._get_url = function (url_pattern) {
        var self = this._instance
        return function () {
            var index, url, url_arg, url_args, _i, _len, _ref;
            _ref = self.url_patterns[url_pattern], url = _ref[0], url_args = _ref[1];
            for (index = _i = 0, _len = url_args.length; _i < _len; index = ++_i) {
                url_arg = url_args[index];
                url = url.replace("%(" + url_arg + ")s", arguments[index] || '');
            }
            return "/" + url;
        };
    };

    Urls.init = function () {
        var name, pattern, self, url_patterns, _i, _len, _ref;
        url_patterns = [
            
                [
                    'account_confirm_email', ['account/confirm_email/%(key)s/', ['key']]
                ],
            
                [
                    'account_delete', ['account/delete/', []]
                ],
            
                [
                    'account_login', ['account/login/', []]
                ],
            
                [
                    'account_logout', ['account/logout/', []]
                ],
            
                [
                    'account_password', ['account/password/', []]
                ],
            
                [
                    'account_password_reset', ['account/password/reset/', []]
                ],
            
                [
                    'account_password_reset_token', ['account/password/reset/%(uidb36)s\u002D%(token)s/', ['uidb36','token']]
                ],
            
                [
                    'account_settings', ['account/settings/', []]
                ],
            
                [
                    'account_signup', ['account/signup/', []]
                ],
            
                [
                    'api_dispatch_detail', ['api/%(api_name)s/%(resource_name)s/%(pk)s/', ['api_name','resource_name','pk']]
                ],
            
                [
                    'api_dispatch_list', ['api/%(api_name)s/%(resource_name)s/', ['api_name','resource_name']]
                ],
            
                [
                    'api_get_multiple', ['api/%(api_name)s/%(resource_name)s/set/%(pk_list)s/', ['api_name','resource_name','pk_list']]
                ],
            
                [
                    'api_get_schema', ['api/%(api_name)s/%(resource_name)s/schema/', ['api_name','resource_name']]
                ],
            
                [
                    'api_v1_top_level', ['api/%(api_name)s/', ['api_name']]
                ],
            
                [
                    'class_index', ['content2/%(model_name)s/%(class_name)s/', ['model_name','class_name']]
                ],
            
                [
                    'content_create', ['content2/add/%(model_name)s/', ['model_name']]
                ],
            
                [
                    'content_delete', ['content2/delete/%(model_name)s/%(pk)s/', ['model_name','pk']]
                ],
            
                [
                    'content_detail', ['content2/%(model_name)s/%(pk)s/%(slug)s', ['model_name','pk','slug']]
                ],
            
                [
                    'content_edit', ['content2/edit/%(model_name)s/%(pk)s/', ['model_name','pk']]
                ],
            
                [
                    'content_index', ['content2/', []]
                ],
            
                [
                    'contribute', ['about/contribute/', []]
                ],
            
                [
                    'dash', ['dashboard', []]
                ],
            
                [
                    'faq', ['about/faq/', []]
                ],
            
                [
                    'filtered_index', ['content2/%(model_name)s/%(kvquery)s/', ['model_name','kvquery']]
                ],
            
                [
                    'home', ['', []]
                ],
            
                [
                    'item_create', ['content/add/%(model_name)s', ['model_name']]
                ],
            
                [
                    'item_delete', ['content/delete/%(model_name)s/%(pk)s', ['model_name','pk']]
                ],
            
                [
                    'item_detail', ['content/%(model_name)s/%(pk)s/%(slug)s', ['model_name','pk','slug']]
                ],
            
                [
                    'item_edit', ['content/edit/%(model_name)s/%(pk)s', ['model_name','pk']]
                ],
            
                [
                    'item_index', ['content', []]
                ],
            
                [
                    'model_index', ['content2/%(model_name)s/', ['model_name']]
                ],
            
                [
                    'profile_detail', ['profiles/profile/%(pk)s/%(slug)s', ['pk','slug']]
                ],
            
                [
                    'profile_edit', ['profiles/edit/', []]
                ],
            
                [
                    'profile_list', ['profiles/', []]
                ],
            
                [
                    'profile_list_all', ['profiles/all/', []]
                ],
            
                [
                    'redis', ['utils/redis', []]
                ],
            
                [
                    'redis_filtered', ['utils/redis/%(class)s', ['class']]
                ],
            
                [
                    'rosetta\u002Ddownload\u002Dfile', ['rosetta/download/', []]
                ],
            
                [
                    'rosetta\u002Dhome', ['rosetta/', []]
                ],
            
                [
                    'rosetta\u002Dlanguage\u002Dselection', ['rosetta/select/%(langid)s/%(idx)s/', ['langid','idx']]
                ],
            
                [
                    'rosetta\u002Dpick\u002Dfile', ['rosetta/pick/', []]
                ],
            
                [
                    'search', ['utils/typeahead', []]
                ],
            
                [
                    'tagged_items', ['content/tag/%(tag_slug)s', ['tag_slug']]
                ],
            
                [
                    'team', ['about/team/', []]
                ],
            
                [
                    'top_categories_json', ['content/%(format)s/top_categories', ['format']]
                ]
            
        ];
        self = this._instance;
        self.url_patterns = {};
        for (_i = 0, _len = url_patterns.length; _i < _len; _i++) {
            _ref = url_patterns[_i], name = _ref[0], pattern = _ref[1];
            self.url_patterns[name] = pattern;
            this[name] = this._get_url(name);
        }
        return self;
    };

    return Urls;
})();

exports.Urls.init();


