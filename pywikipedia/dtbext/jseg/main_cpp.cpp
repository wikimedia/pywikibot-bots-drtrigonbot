

// for all the python stuff in this C to C++ wrapper here
// look at 'bagofwords_classification_python.cpp'

#include "main.hpp"

#include <boost/python.hpp>
#include <boost/python/stl_iterator.hpp>
#include <vector>
//#include <iostream>
//#include <cstdio>

using namespace std;


void worker_python(const boost::python::list& str_list = boost::python::list())
{
    vector<string> strvec;
    if (str_list)
    {
        boost::python::stl_input_iterator<string> begin(str_list), end;
        std::copy( begin, end, back_inserter(strvec) );
    }

    // http://bytes.com/topic/c/answers/127614-best-way-copy-vector-string-char
    // this is a VERY GENERIC WAY TO ADAPT C/C++ CODE TO PYTHON

/*    // print out the strings (just for sanity)
    for (vector<string>::iterator ii=strvec.begin(); ii!=strvec.end(); ++ii)
    cout << *ii;
    cout << endl;
*/

    // allocate memory for an array of character strings
    char** cstr = new char*[strvec.size()];

    // for each string, allocate memory in the character array and copy
    for (unsigned long i=0; i<strvec.size(); i++)
    {
        cstr[i] = new char[strvec[i].size()+1];
        strncpy(cstr[i], strvec[i].c_str(), strvec[i].size());
        cstr[i][strvec[i].size()] = 0;
    }

/*    // print out the newly copied strings
    for (unsigned long i=0; i<strvec.size(); i++) cout << cstr[i];
    cout << endl;
*/

    /* redirecting stdout for python (NOT the C++ std:cout stream!) */
    /* http://www.cplusplus.com/reference/clibrary/cstdio/freopen/ */
    /* http://c-faq.com/stdio/rd.kirby.c (dup, dup2 not available on all OS) */
    fpos_t pos;
    fflush(stdout);
    fgetpos(stdout, &pos);
    int fd = dup(fileno(stdout));
    freopen((strvec[6] + ".stdout").c_str(), "w", stdout);

    // call the actual worker function
    worker(strvec.size(), cstr);

    // reset stdout change (to initial state)
    fflush(stdout);
    dup2(fd, fileno(stdout));
    close(fd);
    clearerr(stdout);
    fsetpos(stdout, &pos);        /* for C9X */

    // free dynamic memory
    for (unsigned long i=0; i<strvec.size(); i++) delete[] cstr[i];
    delete[] cstr;
}

int main (int argc, char *argv[])
{
  // call the actual worker function
  worker(argc, argv);

  return 0;
}


BOOST_PYTHON_MODULE(segdist_cpp)
{
  /*def("name", function_ptr);
  def("name", function_ptr, call_policies);
  def("name", function_ptr, "documentation string");
  def("name", function_ptr, call_policies, "documentation string");*/
  using namespace boost::python;
  def("main", worker_python, "segdist main function");
}
