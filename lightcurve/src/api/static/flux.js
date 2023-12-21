// From Masci+2023 sections 6.4 and 6.5
const SNT = 3.;
const SNU = 5.;

function magdiff2flux_uJy(mag, isdiffpos){
    return Math.pow(10., (-0.4 * (mag - 23.9)) * isdiffpos)
};

function magtot2flux_uJy(mag){
    return Math.pow(10., (-0.4 * (mag - 23.9)))
};

function fluxerr(magerr, flux){
    return Math.abs(magerr) * Math.abs(flux)
};

function flux_uJy2magupperlim(fluxerr){
    return -2.5 * Math.log10(SNU * Math.abs(fluxerr)) + 23.9
};

export { magtot2flux_uJy, magdiff2flux_uJy, fluxerr, flux_uJy2magupperlim }
