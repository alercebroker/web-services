

export class Paginator {
    constructor(data, rows_per_page) {
        this.data = data;
        this.rows_per_page = rows_per_page;
        this._current_page = 1;
        this._total_pages = this.calculate_total_pages();
    }

    set current_page(page) {
        this._current_page = page
    }

    get page_data() {
        return this.data.slice(this.start_index(), this.end_index());
    }

    get total_pages() {
        return this._total_pages
    }

    calculate_total_pages() {
        return Math.ceil(this.data.length / this.rows_per_page);
    }

    start_index() {
        return (this._current_page - 1) * this.rows_per_page;
    }

    end_index() {
        return this.start_index() + this.rows_per_page;
    }

    is_valid_page(page) {
        return page >= 1 && page <= this._total_pages;
    }

    next_page() {
        if (this.is_valid_page(this._current_page + 1)) {
            this._current_page += 1;

            return true;
        }
    }

    previous_page() {
        if (this.is_valid_page(this._current_page - 1)) {
            this._current_page -= 1;

            return true;
        }
    }

}