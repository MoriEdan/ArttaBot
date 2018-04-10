from config.cst import EvaluatorMatrixTypes
from evaluator.Updaters.social_evaluator_not_threaded_update import SocialEvaluatorNotThreadedUpdateThread
from evaluator.Updaters.social_global_updater import SocialGlobalUpdaterThread
from evaluator.evaluator_creator import EvaluatorCreator
from evaluator.evaluator_final import FinalEvaluatorThread
from evaluator.evaluator_matrix import EvaluatorMatrix
from evaluator.evaluator_order_creator import EvaluatorOrderCreator


class Symbol_Evaluator:
    def __init__(self, config, crypto_currency):
        self.crypto_currency = crypto_currency
        self.trader_simulator = None
        self.config = config
        self.notifier = None
        self.traders = None
        self.trader_simulators = None

        self.matrix = EvaluatorMatrix()

        self.social_eval_list = EvaluatorCreator.create_social_eval(self.config, self.crypto_currency)
        self.social_not_threaded_list = EvaluatorCreator.create_social_not_threaded_list(self.social_eval_list)
        self.strategies_eval_list = EvaluatorCreator.create_strategies_eval_list()

        self.social_evaluator_refresh = SocialEvaluatorNotThreadedUpdateThread(self.social_not_threaded_list)
        self.global_social_updater = SocialGlobalUpdaterThread(self)
        self.evaluator_order_creator = EvaluatorOrderCreator()
        self.final_thread = FinalEvaluatorThread(self)

    def start_threads(self):
        self.social_evaluator_refresh.start()
        self.global_social_updater.start()
        self.final_thread.start()

    def stop_threads(self):
        for thread in self.social_eval_list:
            thread.stop()

        self.social_evaluator_refresh.stop()
        self.global_social_updater.stop()
        self.final_thread.stop()

    def join_threads(self):
        for thread in self.social_eval_list:
            thread.join()

        self.social_evaluator_refresh.join()
        self.global_social_updater.join()
        self.final_thread.join()

    def set_notifier(self, notifier):
        self.notifier = notifier

    def set_traders(self, trader):
        self.traders = trader

    def set_trader_simulators(self, simulator):
        self.trader_simulators = simulator

    def update_strategies_eval(self, new_matrix, ignored_evaluator=None):
        for strategies_evaluator in self.strategies_eval_list:
            strategies_evaluator.set_matrix(new_matrix)
            if not strategies_evaluator.get_name() == ignored_evaluator and strategies_evaluator.get_is_evaluable():
                strategies_evaluator.eval()

            # update matrix
            self.matrix.set_eval(EvaluatorMatrixTypes.STRATEGIES, strategies_evaluator.get_name(),
                                 strategies_evaluator.get_eval_note())

    def finalize(self, exchange, symbol):
        self.final_thread.prepare()
        self.final_thread.calculate_final()
        self.final_thread.create_state(exchange, symbol)

    def get_notifier(self):
        return self.notifier

    def get_trader(self, exchange):
        return self.traders[exchange.get_name()]

    def get_trader_simulator(self, exchange):
        return self.trader_simulators[exchange.get_name()]

    def get_final(self):
        return self.final_thread

    def get_matrix(self):
        return self.matrix

    def get_evaluator_creator(self):
        return self.evaluator_order_creator

    def get_strategies_eval_list(self):
        return self.strategies_eval_list

    def get_social_eval_list(self):
        return self.social_eval_list

    def get_social_not_threaded_list(self):
        return self.social_not_threaded_list
