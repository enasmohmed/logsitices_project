import gulp from 'gulp';
import * as sass from 'sass';
import gulpSass from 'gulp-sass';
import concat from 'gulp-concat';
import autoprefixer from 'gulp-autoprefixer';
import cleanCss from 'gulp-clean-css';

const sassCompiler = gulpSass(sass);

const scssFiles = '/home/enas/Enas/logistics/static/assets/scss/**/*.scss';
const cssDest = '/home/enas/Enas/logistics/static/assets/css';

function styles() {
    return gulp.src(scssFiles)
        .pipe(sassCompiler().on('error', sassCompiler.logError))
        .pipe(autoprefixer())
        .pipe(cleanCss())
        .pipe(concat('style.css'))
        .pipe(gulp.dest(cssDest));
}

function watch() {
    gulp.watch(scssFiles, styles);
}

export default gulp.series(styles, watch);
