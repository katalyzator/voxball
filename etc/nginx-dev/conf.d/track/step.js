function track_get_step(req, res) {
    var step = req.headers['X-Track-Step'];
    // req.log("step before " + step);
    if (step != "") {
        step = parseInt(step) + 1;
    }else{
        step = 1;
    }
    // req.log("step after " + step);
    return step;
}
