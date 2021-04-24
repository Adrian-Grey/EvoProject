class CSVStore {
  constructor(strData = "", typeHints = {}) {
    this.entries = [];
    this.headers = [];
    this.typeHints = typeHints;
    this.parseData(strData);
  }
  parseData(rawData) {
    for (let row of rawData.split("\n")) {
      row = row.trim();
      if (!row.length) {
        continue;
      }
      let cols = row.split(",").map(str => str.trim());
      if (!this.headers.length) {
        this.headers = cols.map(name => name.toLowerCase());
      } else {
        let entry = {};
        for (let name of this.headers) {
          let value = cols.shift();
          if (name in this.typeHints) {
            switch (this.typeHints[name]) {
              case "int":
                value = parseInt(value, 10);
                break;
              case "float":
                value = parseFloat(value, 10);
                break;
            }
          }
          entry[name] = value;
        }
        this.entries.push(entry);
      }
    }
  }
  query(params = {}, options = {}) {
    let result = [];
    for (let entry of this.entries) {
      if (options.limit && result.length >= options.limit) {
        break;
      }
      for (let [name, value] of Object.entries(params)) {
        if (entry[name] !== value) {
          continue;
        }
      }
      result.push(entry);
    }
    return result;
  }
}
