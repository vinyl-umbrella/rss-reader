module.exports = {
  pluginOptions: {
    electronBuilder: {
      builderOptions: {
        productName: "rss-reader",
        appId: "com.sample.myapplication",
        win: {
          icon: 'src/assets/app_icon.ico',
          target: [
            {
              target: 'nsis', // 'nsis', 'portable'
              arch: ['x64'] // 'x64', 'ia32'
            }
          ]
        }
      }
    }
  }
}