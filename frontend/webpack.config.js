const path = require('path');

module.exports = {
    entry: './index.js', // index.js 파일을 참조
    output: {
        filename: 'main.js',
        path: path.resolve(__dirname, 'dist'),
    },
    devServer: {
        static: {
            directory: path.join(__dirname, 'public'), // 정적 파일이 위치한 디렉토리
        },
        port: 3001, // 포트를 3001로 변경
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                },
            },
        ],
    },
    resolve: {
        extensions: ['.js', '.jsx'],
    },
}; 