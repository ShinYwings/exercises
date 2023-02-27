#include <iostream>
#include <vector>
#include <string>
#include <random>

#include <opencv4/opencv2/opencv.hpp>
#include <opencv4/opencv2/photo.hpp>
#include <opencv4/opencv2/imgproc.hpp>
#include <opencv4/opencv2/core.hpp>

#include <pybind11/embed.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>


namespace py = pybind11;

using namespace std;

py::dtype determine_np_dtype(int depth)
{
    switch (depth) {
    case CV_8U: return py::dtype::of<uint8_t>();
    case CV_8S: return py::dtype::of<int8_t>();
    case CV_16U: return py::dtype::of<uint16_t>();
    case CV_16S: return py::dtype::of<int16_t>();
    case CV_32S: return py::dtype::of<int32_t>();
    case CV_32F: return py::dtype::of<float>();
    case CV_64F: return py::dtype::of<double>();
    default:
        throw std::invalid_argument("Unsupported data type.");
    }
}

std::vector<std::size_t> determine_shape(cv::Mat& m)
{
    if (m.channels() == 1) {
        return {
            static_cast<size_t>(m.rows)
            , static_cast<size_t>(m.cols)
        };
    }

    return {
        static_cast<size_t>(m.rows)
        , static_cast<size_t>(m.cols)
        , static_cast<size_t>(m.channels())
    };
}

py::capsule make_capsule(cv::Mat& m)
{
    return py::capsule(new cv::Mat(m)
        , [](void *v) { delete reinterpret_cast<cv::Mat*>(v); }
        );
}

py::array mat_to_nparray(cv::Mat& m)
{
    if (!m.isContinuous()) {
        throw std::invalid_argument("Only continuous Mats supported.");
    }

    return py::array(determine_np_dtype(m.depth())
        , determine_shape(m)
        , m.data
        , make_capsule(m));
}

py::array random_tone_map (py::array_t<float>& srcimg, std::string method)
{
    std::random_device rd;
    std::mt19937 gen(rd());

    auto rows = srcimg.shape(0);
    auto cols = srcimg.shape(1);
    auto type = CV_32FC3;
    cv::Mat img(rows, cols, type, (float*)srcimg.data());
    // cv::add(img, cv::Scalar(0.00955794), img); // prevent NaN (this case specified in Laval Sky Database)  

    cv::Mat out;

    if (method == "drago")
    {   
        cout << "in drago" << endl;
        std::uniform_real_distribution<> gamma_rndnum(1.8, 2.2);
        std::uniform_real_distribution<> bias_rndnum(0.7, 0.9);

        auto op = cv::createTonemapDrago(gamma_rndnum(gen), 1.0, bias_rndnum(gen));
        op->process(img,out);
        // out *= 255;
        // out.convertTo(out, CV_8UC3);
        // auto res = mat_to_nparray(out);
        
        // return res;
    }
    else if (method == "reinhard")
    {
        cout << "in reinhard" << endl;
        std::uniform_real_distribution<> gamma_rndnum(1.8, 2.2);
        std::uniform_real_distribution<> intensity_rndnum(-1.0, 1.0);
        std::uniform_real_distribution<> light_adapt_rndnum(0.8, 1.0);
        std::uniform_real_distribution<> color_adapt_rndnum(0.0, 0.2);

        auto op = cv::createTonemapReinhard
                    (gamma_rndnum(gen), intensity_rndnum(gen), 
                       light_adapt_rndnum(gen), color_adapt_rndnum(gen));
        op->process(img,out);

        // out *= 255;
        // out.convertTo(out, CV_8UC3);
        // auto res = mat_to_nparray(out);
        
        // return res;
    }
    // else if (method == "exposure")
    // {
    //     std::uniform_real_distribution<> gamma_rndnum(1.8, 2.2);
    //     std::uniform_real_distribution<> low_perc(0., 15.);
    //     std::uniform_real_distribution<> high_perc(85., 100.);
    // } 
    else
    {
        cout << "in mantiuk" << endl;
        //  if (method == "mantiuk")
        std::uniform_real_distribution<> gamma_rndnum(1.8, 2.2);
        std::uniform_real_distribution<> scale_rndnum(0.65, 0.85);

        auto op = cv::createTonemapMantiuk
                    (gamma_rndnum(gen), scale_rndnum(gen),
                        1.0);
        op->process(img,out);
    }   

    out *= 255;
    out.convertTo(out, CV_8UC3);
    auto res = mat_to_nparray(out);
    
    return res;
}

PYBIND11_MODULE(random_tone_map, module_handle) {
    module_handle.def("random_tone_map", &random_tone_map);
}