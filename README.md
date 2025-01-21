# Adobe-Package-Downloader

A Python script for downloading Adobe software packages across different platforms (Windows x64, Windows ARM64, and macOS).

## Credits
As far as I know, this script was started by the user "ayyybe" on github gist.
Here are the links to the used sources:
* https://gist.github.com/ayyybe/a5f01c6f40020f9a7bc4939beeb2df1d

This script was modified from the original macOS version. It now supports Windows platforms, while macOS users may need to test and make modifications as needed.

The script and README were written with assistance from Claude.

## Features

- Support for multiple platforms:
  - Windows ARM64 (Windows 11 ARM)
  - Windows x64
  - macOS (Intel/Apple Silicon)
- Download resume capability
- Progress tracking for downloads
- Auto-retry mechanism
- Multiple language support
- Command-line interface support

## Prerequisites

- Python 3.7+
- Required Python packages:
```bash
pip install requests urllib3
```

## Usage

### Basic Usage

1. Run the script:
```bash
python adobe_package_generator.py
```

2. Follow the interactive prompts to:
   - Select platform
   - Choose product
   - Select version
   - Choose language
   - Select download location

### Command Line Arguments

You can also use command line arguments for automation:

```bash
python adobe_package_generator.py -p winarm64 -s PHSP -v 25.0 -l en_US -d /download/path
```

Available arguments:
- `-p, --platform`: Platform (winarm64, win64, osx10-64)
- `-s, --sapCode`: SAP code for desired product (e.g., PHSP for Photoshop)
- `-v, --version`: Version of desired product (e.g., 25.0)
- `-l, --installLanguage`: Language code (e.g., en_US)
- `-d, --destination`: Directory to download installation files to

### Common SAP Codes

- `PHSP`: Adobe Photoshop
- `ILST`: Adobe Illustrator
- `AEFT`: Adobe After Effects
- `PPRO`: Adobe Premiere Pro
- `LRCC`: Adobe Lightroom
- `FLPR`: Adobe Animate

## Language Support

Supported language codes include:
- `en_US`: English (US)
- `zh_CN`: Chinese (Simplified)
- `zh_TW`: Chinese (Traditional)
- `ja_JP`: Japanese
- `ko_KR`: Korean
- `de_DE`: German
- `es_ES`: Spanish
- `fr_FR`: French
And many more...

## Notes

1. Not all Adobe products are available for all platforms
2. Some older versions might not be available for certain platforms
3. Downloaded packages will be organized in folders by product
4. The script automatically generates a driver.xml file for installation

## Troubleshooting

### SSL Certificate Issues
If you encounter SSL certificate errors, the script automatically handles them. However, this is not recommended for production use.

### Download Interruptions
The script includes resume capability. If a download is interrupted, simply run the script again with the same parameters.

## Disclaimer

This tool is for educational purposes only. Make sure you have the right to download and use Adobe software packages.

## Contributing

Feel free to open issues or submit pull requests for improvements.

## License

MIT License

## Support

If you encounter any problems or have suggestions, please open an issue on GitHub.

---

# Adobe 软件包下载工具

一个用于下载 Adobe 软件包的 Python 脚本，支持不同平台（Windows x64、Windows ARM64 和 macOS）。

## 致谢
据我所知，这个脚本最初由 GitHub 用户 "ayyybe" 在 gist 上创建。
以下是原始源码链接：
* https://gist.github.com/ayyybe/a5f01c6f40020f9a7bc4939beeb2df1d

本脚本由原版 macOS 脚本修改而来，现已支持 Windows 平台。macOS 用户可能需要进行测试和适当修改才能使用。

脚本和 README 在 Claude 的协助下编写完成。

## 主要特性

- 支持多个平台：
  - Windows ARM64 (Windows 11 ARM)
  - Windows x64
  - macOS (Intel/Apple Silicon)
- 支持断点续传
- 下载进度显示
- 自动重试机制
- 多语言支持
- 命令行界面支持

## 运行环境要求

- Python 3.7+
- 需要安装的 Python 包：
```bash
pip install requests urllib3
```

## 使用方法

### 基本用法

1. 运行脚本：
```bash
python adobe_package_generator.py
```

2. 按提示依次选择：
   - 选择平台
   - 选择产品
   - 选择版本
   - 选择语言
   - 选择下载位置

### 命令行参数

也可以使用命令行参数来自动化操作：

```bash
python adobe_package_generator.py -p winarm64 -s PHSP -v 25.0 -l en_US -d /download/path
```

可用参数：
- `-p, --platform`：平台 (winarm64, win64, osx10-64)
- `-s, --sapCode`：产品 SAP 代码（如 PHSP 代表 Photoshop）
- `-v, --version`：产品版本（如 25.0）
- `-l, --installLanguage`：语言代码（如 zh_CN）
- `-d, --destination`：下载文件保存目录

### 常用 SAP 代码

- `PHSP`：Adobe Photoshop
- `ILST`：Adobe Illustrator
- `AEFT`：Adobe After Effects
- `PPRO`：Adobe Premiere Pro
- `LRCC`：Adobe Lightroom
- `FLPR`：Adobe Animate

## 支持的语言

支持的语言代码包括：
- `en_US`：英语（美国）
- `zh_CN`：中文（简体）
- `zh_TW`：中文（繁体）
- `ja_JP`：日语
- `ko_KR`：韩语
- `de_DE`：德语
- `es_ES`：西班牙语
- `fr_FR`：法语
等等...

## 注意事项

1. 并非所有 Adobe 产品都支持所有平台
2. 某些旧版本可能不支持特定平台
3. 下载的文件会按产品分文件夹存放
4. 脚本会自动生成用于安装的 driver.xml 文件

## 故障排除

### SSL 证书问题
如果遇到 SSL 证书错误，脚本会自动处理。但这种处理方式不建议在生产环境中使用。

### 下载中断
脚本支持断点续传。如果下载中断，只需使用相同参数重新运行脚本即可。

## 免责声明

此工具仅用于教育目的。请确保您有权下载和使用 Adobe 软件包。

## 贡献

欢迎提出问题或提交改进建议。

## 许可证

MIT 许可证

## 支持

如果遇到问题或有建议，请在 GitHub 上提出 issue。
