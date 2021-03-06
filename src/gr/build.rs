// build.rs

extern crate gcc;

fn main() {
    gcc::Config::new()
        .cpp(true)
        .cpp_link_stdlib(Some("stdc++"))
        .flag("-msse3")
        .flag("-O3")
        .flag("-std=c++11")
        .flag("-march=native")
        .flag("-fno-lto")
        .file("src/gaol_wrap.cc")
        .compile("librustgaol.a");
}
