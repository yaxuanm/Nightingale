@echo off
chcp 65001
echo ========================================
echo 前端依赖更新脚本
echo ========================================
echo.

echo 检查并更新前端依赖...
cd ambiance-weaver-react

echo 1. 检查当前依赖版本...
npm list --depth=0

echo.
echo 2. 更新过时的依赖...
echo 更新 workbox 相关包...
npm install workbox-webpack-plugin@latest --save-dev
npm install workbox-core@latest --save-dev
npm install workbox-expiration@latest --save-dev
npm install workbox-precaching@latest --save-dev
npm install workbox-routing@latest --save-dev
npm install workbox-strategies@latest --save-dev

echo 更新 SVGO...
npm install svgo@latest --save-dev

echo 更新 Babel 插件...
npm install @babel/plugin-transform-private-methods@latest --save-dev
npm install @babel/plugin-transform-numeric-separator@latest --save-dev
npm install @babel/plugin-transform-class-properties@latest --save-dev
npm install @babel/plugin-transform-nullish-coalescing-operator@latest --save-dev
npm install @babel/plugin-transform-private-property-in-object@latest --save-dev
npm install @babel/plugin-transform-optional-chaining@latest --save-dev

echo 更新其他过时包...
npm install @rollup/plugin-terser@latest --save-dev
npm install @eslint/config-array@latest --save-dev
npm install @eslint/object-schema@latest --save-dev
npm install @jridgewell/sourcemap-codec@latest --save-dev

echo.
echo 3. 清理并重新安装...
npm cache clean --force
npm install

echo.
echo 4. 检查更新后的依赖...
npm list --depth=0

echo.
echo ========================================
echo ✓ 前端依赖更新完成！
echo ========================================
echo.
echo 主要更新:
echo - workbox 相关包升级到最新版本
echo - SVGO 升级到 v2.x.x
echo - Babel 插件升级到 transform 版本
echo - 其他过时包升级到推荐版本
echo.
echo 现在可以运行 npm start 测试功能
cd ..
pause 