%bcond_without tests
%bcond_without weak_deps

%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%global __provides_exclude_from ^/opt/ros/jazzy/.*$
%global __requires_exclude_from ^/opt/ros/jazzy/.*$
%global debug_package %{nil}

Name:           ros-jazzy-gmock-vendor
Version:        1.14.9000
Release:        0%{?dist}%{?release_suffix}
Summary:        ROS gmock_vendor package

License:        BSD
Source0:        %{name}-%{version}.tar.gz

Requires:       ros-jazzy-gtest-vendor
BuildRequires:  cmake

%description
The package provides GoogleMock.

%prep
%autosetup -p1

%build
yum install ros-jazzy-ament-package -y
# 修复 PYTHONPATH 环境变量
export PYTHONPATH=/opt/ros/jazzy/lib/python3.11/site-packages:$PYTHONPATH

# 修复 CMAKE_PREFIX_PATH 和 PKG_CONFIG_PATH
export CMAKE_PREFIX_PATH=/opt/ros/jazzy
export PKG_CONFIG_PATH=/opt/ros/jazzy/lib/pkgconfig

# 输出环境变量以验证设置
echo "PYTHONPATH: $PYTHONPATH"
echo "CMAKE_PREFIX_PATH: $CMAKE_PREFIX_PATH"
echo "PKG_CONFIG_PATH: $PKG_CONFIG_PATH"

# 验证 ament_package 是否可用
python3 -c "import ament_package" || { echo "ament_package not found"; exit 1; }

# 创建构建目录并进入
mkdir -p .obj-%{_target_platform} && cd .obj-%{_target_platform}
%cmake3 \
    -UINCLUDE_INSTALL_DIR \
    -ULIB_INSTALL_DIR \
    -USYSCONF_INSTALL_DIR \
    -USHARE_INSTALL_PREFIX \
    -ULIB_SUFFIX \
    -DCMAKE_INSTALL_PREFIX="/opt/ros/jazzy" \
    -DCMAKE_PREFIX_PATH="/opt/ros/jazzy" \
    -DSETUPTOOLS_DEB_LAYOUT=OFF \
%if !0%{?with_tests}
    -DBUILD_TESTING=OFF \
%endif
    ..

%make_build

%install
# In case we're installing to a non-standard location, look for a setup.sh
# in the install tree and source it.  It will set things like
# CMAKE_PREFIX_PATH, PKG_CONFIG_PATH, and PYTHONPATH.
if [ -f "/usr/setup.sh" ]; then . "/usr/setup.sh"; fi
%make_install -C .obj-%{_target_platform}

%if 0%{?with_tests}
%check
# 检查是否存在测试目标
TEST_TARGET=$(%__make -qp -C .obj-%{_target_platform} | sed "s/^\(test\|check\):.*/\\1/;t f;d;:f;q0")
if [ -n "$TEST_TARGET" ]; then
    if [ -f "/opt/ros/jazzy/setup.sh" ]; then . "/opt/ros/jazzy/setup.sh"; fi
    CTEST_OUTPUT_ON_FAILURE=1 \
        %make_build -C .obj-%{_target_platform} $TEST_TARGET || echo "Tests failed but ignored"
else
    echo "No tests to run"
fi
%endif

%files
/opt/ros/jazzy/*

%changelog
* Sat Dec 14 2024 Scott K Logan <scott@openrobotics.org> - 1.14.9000-0
- Autogenerated by Bloom

