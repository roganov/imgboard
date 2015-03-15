var gulp = require('gulp'),
    $ = require('gulp-load-plugins')();


var staticSrc = './static/src/',
    staticVendor = './static/vendor/';

var vendor = {
    'jquery-ui': {
        js: 'jquery-ui/jquery-ui.js',
        images: 'jquery-ui/images/*'
    },
    'bootstrap': {
        js: ['bootstrap/js/modal.js'],
        fonts: 'bootstrap/fonts/*'
    }
};

var src = {
    js: [staticSrc + 'js/!(app.js|app.coffee)',
         staticSrc + 'js/+(app.js|app.coffee)'],
    css: [staticSrc + 'css/style.less']
};

function vendorPaths(type) {
    var paths = [];
    for (var plugin in vendor) {
        if (vendor.hasOwnProperty(plugin) && vendor[plugin][type]) {
            var p = vendor[plugin][type];
            if (!p) {
                continue;
            }
            if (!Array.isArray(p)) {
                p = [p];
            }
            for (var i = 0, len = p.length; i < len; i ++) {
                paths.push(staticVendor + p[i]);
            }
        }
    }
    return paths;
}

var jsFiles = vendorPaths('js').concat(src.js),
    fontFiles = vendorPaths('fonts'),
    imageFiles = vendorPaths('images'),
    cssFiles = src.css,
    jqueryFile = staticVendor + 'jquery/jquery-2.1.3.min.js';

var dest = './static/dist',
    destJS = dest + '/js',
    destCSS = dest + '/css',
    destFonts = dest + '/fonts',
    destImages = dest + '/images';

gulp.task('jquery', function() {
    gulp.src(jqueryFile)
        .pipe(gulp.dest(destJS));
});

gulp.task('js', function() {
    gulp.src(jsFiles)
        .pipe($.if('/**/*.coffee', $.coffee()))
        .pipe($.concat('app.js'))
        .pipe($.uglify())
        .pipe(gulp.dest(destJS));
});

gulp.task('css', function() {
    gulp.src(cssFiles)
        .pipe($.if(/\.less$/, $.less()))
        .pipe($.concat('style.css'))
        .pipe($.minifyCss())
        .pipe(gulp.dest(destCSS));
});

gulp.task('fonts', function() {
    gulp.src(fontFiles)
        .pipe(gulp.dest(destFonts));
});

gulp.task('images', function() {
    gulp.src(imageFiles)
        .pipe(gulp.dest(destImages));
});

gulp.task('build', ['jquery', 'js', 'css', 'fonts', 'images']);

gulp.task('watch', ['build'], function() {
    gulp.watch(cssFiles, ['css']);
    gulp.watch(jsFiles, ['js']);
});

gulp.task('default', ['watch']);