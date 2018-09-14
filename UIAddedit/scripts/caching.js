var _Caching = (function () {
    var local_assets = [];
    return {
        GetUrlExtension: function () {
            var urlextension = '';
            if (!_Settings.enableCache) {
                urlextension = "?npage=" + Math.random();
            }
            return urlextension;
        },
        InitPageCaching: function () {
            var _htmlData = _Navigator.Get();
            for (var i in _htmlData) {
                var pageUrl = _Settings.dataRoot + _htmlData[i].dataurl;
                this.Cache(pageUrl);
                if (_htmlData[i].questions.length > 0) {
                    for (var j = 0; j < _htmlData[i].questions.length; j++) {
                        var pageUrl = _Settings.dataRoot + _htmlData[i].questions[j].dataurl;
                        this.Cache(pageUrl);
                    }
                }
            }
        },
        InitAssetsCaching: function () {
            for (var k = 0; k < local_assets.length; k++) {
                var pageUrl = _Settings.assetsRoot + local_assets[k];
                this.Cache(pageUrl);
            }
        },
        Cache: function (url) {
            var xhr = new XMLHttpRequest();
            xhr.open("GET", url, true);
            xhr.send(null);
        }
    }
})();