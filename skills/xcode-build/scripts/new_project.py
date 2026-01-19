#!/usr/bin/env python3
"""
new_project.py - Create new SwiftUI + SwiftData iOS project.

Usage:
    python new_project.py MyApp --bundle-id com.company.myapp
    python new_project.py MyApp --bundle-id com.company.myapp --team TEAMID123
    python new_project.py MyApp --bundle-id com.company.myapp --min-ios 17.0
    python new_project.py MyApp --bundle-id com.company.myapp --output ./projects
"""

import argparse
import os
import sys
from pathlib import Path
from xcode_utils import ensure_dir, to_pascal_case


# Project file templates
PBXPROJ_TEMPLATE = '''// !$*UTF8*$!
{
	archiveVersion = 1;
	classes = {
	};
	objectVersion = 56;
	objects = {

/* Begin PBXBuildFile section */
		__APP_SWIFT_REF__1 /* __NAME__App.swift in Sources */ = {isa = PBXBuildFile; fileRef = __APP_SWIFT_REF__ /* __NAME__App.swift */; };
		__CONTENT_VIEW_REF__1 /* ContentView.swift in Sources */ = {isa = PBXBuildFile; fileRef = __CONTENT_VIEW_REF__ /* ContentView.swift */; };
		__ASSETS_REF__1 /* Assets.xcassets in Resources */ = {isa = PBXBuildFile; fileRef = __ASSETS_REF__ /* Assets.xcassets */; };
/* End PBXBuildFile section */

/* Begin PBXFileReference section */
		__APP_REF__ /* __NAME__.app */ = {isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = "__NAME__.app"; sourceTree = BUILT_PRODUCTS_DIR; };
		__APP_SWIFT_REF__ /* __NAME__App.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = "__NAME__App.swift"; sourceTree = "<group>"; };
		__CONTENT_VIEW_REF__ /* ContentView.swift */ = {isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = "ContentView.swift"; sourceTree = "<group>"; };
		__ASSETS_REF__ /* Assets.xcassets */ = {isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; };
/* End PBXFileReference section */

/* Begin PBXGroup section */
		__MAIN_GROUP__ = {
			isa = PBXGroup;
			children = (
				__SOURCE_GROUP__ /* __NAME__ */,
				__PRODUCTS_GROUP__ /* Products */,
			);
			sourceTree = "<group>";
		};
		__PRODUCTS_GROUP__ /* Products */ = {
			isa = PBXGroup;
			children = (
				__APP_REF__ /* __NAME__.app */,
			);
			name = Products;
			sourceTree = "<group>";
		};
		__SOURCE_GROUP__ /* __NAME__ */ = {
			isa = PBXGroup;
			children = (
				__APP_SWIFT_REF__ /* __NAME__App.swift */,
				__CONTENT_VIEW_REF__ /* ContentView.swift */,
				__ASSETS_REF__ /* Assets.xcassets */,
			);
			path = "__NAME__";
			sourceTree = "<group>";
		};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
		__TARGET_REF__ /* __NAME__ */ = {
			isa = PBXNativeTarget;
			buildConfigurationList = __BUILD_CONFIG_LIST__;
			buildPhases = (
				__SOURCES_PHASE__ /* Sources */,
				__RESOURCES_PHASE__ /* Resources */,
			);
			buildRules = (
			);
			dependencies = (
			);
			name = "__NAME__";
			productName = "__NAME__";
			productReference = __APP_REF__ /* __NAME__.app */;
			productType = "com.apple.product-type.application";
		};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
		__PROJECT_REF__ /* Project object */ = {
			isa = PBXProject;
			attributes = {
				BuildIndependentTargetsInParallel = 1;
				LastSwiftUpdateCheck = 1520;
				LastUpgradeCheck = 1520;
				TargetAttributes = {
					__TARGET_REF__ = {
						CreatedOnToolsVersion = 15.2;
					};
				};
			};
			buildConfigurationList = __PROJECT_BUILD_CONFIG_LIST__;
			compatibilityVersion = "Xcode 14.0";
			developmentRegion = en;
			hasScannedForEncodings = 0;
			knownRegions = (
				en,
				Base,
			);
			mainGroup = __MAIN_GROUP__;
			productRefGroup = __PRODUCTS_GROUP__ /* Products */;
			projectDirPath = "";
			projectRoot = "";
			targets = (
				__TARGET_REF__ /* __NAME__ */,
			);
		};
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
		__RESOURCES_PHASE__ /* Resources */ = {
			isa = PBXResourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				__ASSETS_REF__1 /* Assets.xcassets in Resources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		};
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
		__SOURCES_PHASE__ /* Sources */ = {
			isa = PBXSourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				__CONTENT_VIEW_REF__1 /* ContentView.swift in Sources */,
				__APP_SWIFT_REF__1 /* __NAME__App.swift in Sources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		};
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
		__DEBUG_CONFIG__ /* Debug */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEBUG_INFORMATION_FORMAT = dwarf;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_TESTABILITY = YES;
				GCC_DYNAMIC_NO_PIC = NO;
				GCC_OPTIMIZATION_LEVEL = 0;
				GCC_PREPROCESSOR_DEFINITIONS = (
					"DEBUG=1",
					"$(inherited)",
				);
				GENERATE_INFOPLIST_FILE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = __MIN_IOS__;
				MARKETING_VERSION = 1.0;
				MTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;
				ONLY_ACTIVE_ARCH = YES;
				PRODUCT_BUNDLE_IDENTIFIER = "__BUNDLE_ID__";
				PRODUCT_NAME = "$(TARGET_NAME)";
				SDKROOT = iphoneos;
				SWIFT_ACTIVE_COMPILATION_CONDITIONS = "DEBUG $(inherited)";
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_OPTIMIZATION_LEVEL = "-Onone";
				SWIFT_STRICT_CONCURRENCY = complete;
				SWIFT_VERSION = 6.0;
				TARGETED_DEVICE_FAMILY = "1,2";
				__TEAM_SETTING__
			};
			name = Debug;
		};
		__RELEASE_CONFIG__ /* Release */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				ENABLE_NS_ASSERTIONS = NO;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				GENERATE_INFOPLIST_FILE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = __MIN_IOS__;
				MARKETING_VERSION = 1.0;
				MTL_ENABLE_DEBUG_INFO = NO;
				PRODUCT_BUNDLE_IDENTIFIER = "__BUNDLE_ID__";
				PRODUCT_NAME = "$(TARGET_NAME)";
				SDKROOT = iphoneos;
				SWIFT_COMPILATION_MODE = wholemodule;
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_STRICT_CONCURRENCY = complete;
				SWIFT_VERSION = 6.0;
				TARGETED_DEVICE_FAMILY = "1,2";
				VALIDATE_PRODUCT = YES;
				__TEAM_SETTING__
			};
			name = Release;
		};
		__PROJECT_DEBUG_CONFIG__ /* Debug */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
			};
			name = Debug;
		};
		__PROJECT_RELEASE_CONFIG__ /* Release */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
			};
			name = Release;
		};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
		__BUILD_CONFIG_LIST__ /* Build configuration list for PBXNativeTarget "__NAME__" */ = {
			isa = XCConfigurationList;
			buildConfigurations = (
				__DEBUG_CONFIG__ /* Debug */,
				__RELEASE_CONFIG__ /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		};
		__PROJECT_BUILD_CONFIG_LIST__ /* Build configuration list for PBXProject "__NAME__" */ = {
			isa = XCConfigurationList;
			buildConfigurations = (
				__PROJECT_DEBUG_CONFIG__ /* Debug */,
				__PROJECT_RELEASE_CONFIG__ /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		};
/* End XCConfigurationList section */
	};
	rootObject = __PROJECT_REF__ /* Project object */;
}
'''


def generate_uuid():
    """Generate Xcode-style UUID."""
    import random
    return ''.join(random.choices('0123456789ABCDEF', k=24))


def create_app_swift(name: str) -> str:
    """Generate main app file."""
    return f'''import SwiftUI
import SwiftData

@main
struct {name}App: App {{
    var sharedModelContainer: ModelContainer = {{
        let schema = Schema([
            // Add your @Model types here
        ])
        let modelConfiguration = ModelConfiguration(schema: schema, isStoredInMemoryOnly: false)

        do {{
            return try ModelContainer(for: schema, configurations: [modelConfiguration])
        }} catch {{
            fatalError("Could not create ModelContainer: \\(error)")
        }}
    }}()

    var body: some Scene {{
        WindowGroup {{
            ContentView()
                .accessibilityIdentifier("screen_main")
        }}
        .modelContainer(sharedModelContainer)
    }}
}}
'''


def create_content_view(name: str) -> str:
    """Generate ContentView."""
    return f'''import SwiftUI
import SwiftData

struct ContentView: View {{
    @Environment(\\.modelContext) private var modelContext

    var body: some View {{
        NavigationStack {{
            VStack {{
                Image(systemName: "globe")
                    .imageScale(.large)
                    .foregroundStyle(.tint)
                Text("Hello, {name}!")
            }}
            .padding()
            .navigationTitle("{name}")
            .accessibilityIdentifier("screen_content")
        }}
    }}
}}

#Preview {{
    ContentView()
        .modelContainer(for: [], inMemory: true)
}}
'''


def create_assets_contents() -> str:
    """Generate Assets.xcassets Contents.json."""
    return '''{
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
'''


def create_appicon_contents() -> str:
    """Generate AppIcon.appiconset Contents.json."""
    return '''{
  "images" : [
    {
      "idiom" : "universal",
      "platform" : "ios",
      "size" : "1024x1024"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
'''


def create_accent_color_contents() -> str:
    """Generate AccentColor.colorset Contents.json."""
    return '''{
  "colors" : [
    {
      "idiom" : "universal"
    }
  ],
  "info" : {
    "author" : "xcode",
    "version" : 1
  }
}
'''


def main():
    parser = argparse.ArgumentParser(description="Create new SwiftUI + SwiftData project")
    parser.add_argument("name", help="Project name")
    parser.add_argument("--bundle-id", required=True, help="Bundle identifier")
    parser.add_argument("--team", help="Development team ID")
    parser.add_argument("--min-ios", default="17.0", help="Minimum iOS version (default: 17.0)")
    parser.add_argument("--output", "-o", help="Output directory (default: current)")
    args = parser.parse_args()

    name = to_pascal_case(args.name)
    output_dir = Path(args.output) if args.output else Path.cwd()
    project_dir = output_dir / name
    
    if project_dir.exists():
        print(f"Error: Directory already exists: {project_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"📦 Creating project: {name}")
    print(f"   Bundle ID: {args.bundle_id}")
    print(f"   Min iOS: {args.min_ios}")

    # Create directory structure
    ensure_dir(project_dir)
    ensure_dir(project_dir / f"{name}.xcodeproj")
    ensure_dir(project_dir / name)
    ensure_dir(project_dir / name / "Models")
    ensure_dir(project_dir / name / "Views")
    ensure_dir(project_dir / name / "Services")
    ensure_dir(project_dir / name / "Resources")
    ensure_dir(project_dir / name / "Assets.xcassets" / "AppIcon.appiconset")
    ensure_dir(project_dir / name / "Assets.xcassets" / "AccentColor.colorset")
    ensure_dir(project_dir / f"{name}Tests")
    ensure_dir(project_dir / f"{name}UITests")

    # Generate UUIDs
    uuids = {
        "__PROJECT_REF__": generate_uuid(),
        "__MAIN_GROUP__": generate_uuid(),
        "__PRODUCTS_GROUP__": generate_uuid(),
        "__SOURCE_GROUP__": generate_uuid(),
        "__TARGET_REF__": generate_uuid(),
        "__APP_REF__": generate_uuid(),
        "__APP_SWIFT_REF__": generate_uuid(),
        "__CONTENT_VIEW_REF__": generate_uuid(),
        "__ASSETS_REF__": generate_uuid(),
        "__SOURCES_PHASE__": generate_uuid(),
        "__RESOURCES_PHASE__": generate_uuid(),
        "__BUILD_CONFIG_LIST__": generate_uuid(),
        "__PROJECT_BUILD_CONFIG_LIST__": generate_uuid(),
        "__DEBUG_CONFIG__": generate_uuid(),
        "__RELEASE_CONFIG__": generate_uuid(),
        "__PROJECT_DEBUG_CONFIG__": generate_uuid(),
        "__PROJECT_RELEASE_CONFIG__": generate_uuid(),
    }

    # Generate project.pbxproj
    pbxproj = PBXPROJ_TEMPLATE
    for key, value in uuids.items():
        pbxproj = pbxproj.replace(key, value)
    pbxproj = pbxproj.replace("__NAME__", name)
    pbxproj = pbxproj.replace("__BUNDLE_ID__", args.bundle_id)
    pbxproj = pbxproj.replace("__MIN_IOS__", args.min_ios)
    
    team_setting = f'DEVELOPMENT_TEAM = {args.team};' if args.team else ""
    pbxproj = pbxproj.replace("__TEAM_SETTING__", team_setting)

    # Write files
    (project_dir / f"{name}.xcodeproj" / "project.pbxproj").write_text(pbxproj)
    (project_dir / name / f"{name}App.swift").write_text(create_app_swift(name))
    (project_dir / name / "ContentView.swift").write_text(create_content_view(name))
    (project_dir / name / "Assets.xcassets" / "Contents.json").write_text(create_assets_contents())
    (project_dir / name / "Assets.xcassets" / "AppIcon.appiconset" / "Contents.json").write_text(create_appicon_contents())
    (project_dir / name / "Assets.xcassets" / "AccentColor.colorset" / "Contents.json").write_text(create_accent_color_contents())

    # Create placeholder files
    (project_dir / name / "Models" / ".gitkeep").touch()
    (project_dir / name / "Views" / ".gitkeep").touch()
    (project_dir / name / "Services" / ".gitkeep").touch()

    print(f"✅ Project created at: {project_dir}")
    print(f"\nNext steps:")
    print(f"  cd {project_dir}")
    print(f"  open {name}.xcodeproj")


if __name__ == "__main__":
    main()
