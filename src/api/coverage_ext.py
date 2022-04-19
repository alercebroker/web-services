import atexit


class Coverage(object):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        import coverage

        app.logger.info("Using Coverage Extension")
        app.coverage = coverage.Coverage(
            data_file="/coverage-output/.coverage", source=["src/"]
        )
        app.coverage.start()
        atexit.register(self.save_coverage)

    def save_coverage(self, *args, **kwargs):
        self.app.logger.info("Saving Coverage Reports")
        self.app.coverage.stop()
        self.app.coverage.save()
        self.app.coverage.xml_report(outfile="/coverage-output/coverage.xml")
