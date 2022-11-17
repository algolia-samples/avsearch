interface Number {
  toTimeString() : string;
}

Number.prototype.toTimeString = function (): string {
  const sec_num = parseInt(this, 10); // don't forget the second param
  const hours   = Math.floor(sec_num / 3600);
  const minutes = Math.floor((sec_num - (hours * 3600)) / 60);
  const seconds = sec_num - (hours * 3600) - (minutes * 60);

  const hoursString = ( hours < 10 ? '0'+hours.toString() : hours.toString() );
  const minutesString = ( minutes < 10 ? '0'+minutes.toString() : minutes.toString() );
  const secondsString = ( seconds < 10 ? '0'+seconds.toString() : seconds.toString() );
  return ( hours > 0 ? 
    hoursString+':'+minutesString+':'+secondsString :
    minutesString+':'+secondsString
  );
}

