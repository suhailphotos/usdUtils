# usdUtils

Welcome to usdUtils, a repository for experimenting with USD (Universal Scene Description) related tools. This repository is dedicated to developing tools for importing, converting, and manipulating assets within the context of USD workflows.

## Purpose

The purpose of this repository is to explore and develop utilities that streamline the process of working with USD files and assets. This includes:

- Importing assets from various formats into USD.
- Converting existing assets to USD format.
- Building tools for organizing and managing USD projects.
- Implementing workflows for efficient collaboration and version control with USD files.

## Folder Structure

To maintain consistency and organization within USD projects, this repository follows a recommended folder structure for organizing assets, shots, sequences, configurations, and outputs. The folder structure used in this repository is as follows:

```markdown
├── assets
│   ├── `type`
│   │   ├── _template
│   │   │   ├── _publish
│   │   │   └── scene_files
│   │   └── bridge_structure
│   │       ├── _publish
│   │       ├── lkdev
│   │       │   ├── _publish
│   │       │   └── scene_files
│   │       ├── model
│   │       │   ├── _publish
│   │       │   └── scene_files
│   │       └── text
│   │           ├── _publish
│   │           │   └── v004
│   │           │       ├── 2k
│   │           │       └── 4k
│   │           └── scene_files
│   ├── lgt
│   │   ├── hdri
│   │   │   ├── _publish
│   │   │   └── scene_files
│   │   └── light_filters
│   │       ├── _publish
│   │       └── scene_files
│   └── veh
│       ├── _template
│       │   ├── _publish
│       │   └── scene_files
│       ├── bomber
│       │   └── _publish
│       │       └── data
│       │           └── textures
│       ├── cruiser
│       │   ├── _publish
│       │   ├── lkdev
│       │   │   ├── _publish
│       │   │   └── scene_files
│       │   ├── model
│       │   │   ├── _publish
│       │   │   └── scene_files
│       │   └── text
│       │       ├── _publish
│       │       │   └── v003
│       │       │       ├── 2k
│       │       │       └── 4k
│       │       └── scene_files
│       └── transporter
│           ├── _publish
│           ├── lkdev
│           │   ├── _publish
│           │   └── scene_files
│           ├── model
│           │   ├── _publish
│           │   └── scene_files
│           └── text
│               ├── _publish
│               │   └── v020
│               │       ├── 2k
│               │       └── 4k
│               └── scene_files
└── shots
    ├── `seq`
    │   ├── 010
    │   │   ├── _publish
    │   │   ├── anim
    │   │   │   ├── _publish
    │   │   │   └── scene_files
    │   │   ├── comp
    │   │   │   ├── _publish
    │   │   │   └── scene_files
    │   │   ├── layout
    │   │   │   ├── _publish
    │   │   │   └── scene_files
    │   │   ├── lighting
    │   │   │   ├── _publish
    │   │   │   ├── _renders
    │   │   │   └── scene_files
    │   │   └── matchmove
    │   │       ├── _publish
    │   │       └── scene_files
    │   └── _shot_template
    │       ├── _publish
    │       ├── anim
    │       │   ├── _publish
    │       │   └── scene_files
    │       ├── comp
    │       │   ├── _publish
    │       │   └── scene_files
    │       ├── layout
    │       │   ├── _publish
    │       │   └── scene_files
    │       └── lighting
    │           ├── _publish
    │           └── scene_files
    └── `seq`
        └── scene_files
            └── usd
                ├── references
                ├── sublayers
                ├── usd_flatten
                └── usd_format

```


This structure provides a clear organization for managing assets, shots, sequences, configurations, and outputs within a USD project.

## Contributions

Contributions to usdUtils are welcome! If you have ideas for new tools, improvements to existing ones, or bug fixes, feel free to open an issue or pull request. Let's collaborate to make USD workflows more efficient and accessible.

## License

This project is licensed under the [MIT License](LICENSE).

