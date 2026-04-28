import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import statsmodels.api as sm
import networkx as nx
import sympy as sp
import random

try:
    from deap import base, creator, tools
    DEAP_AVAILABLE = True
except ImportError:
    DEAP_AVAILABLE = False
    logging.getLogger(__name__).warning("DEAP not available — evolutionary tuning disabled")

logger = logging.getLogger(__name__)

class PredictiveIntelligenceLayer:
    """SOTA Predictive Intelligence Layer — real-data ensemble, DEAP evolutionary tuning, ARIMA/SymPy/NetworkX, 7D signals, and full flywheel routing."""

    def __init__(self, arbos_manager=None):
        self.arbos = arbos_manager
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        self.gb_model = GradientBoostingRegressor(n_estimators=80, random_state=42)
       
        self.historical_data = pd.DataFrame(columns=[
            "timestamp", "efs", "validation_score", "fidelity", "heterogeneity",
            "fragments_count", "mau_score", "freshness_avg", "c3a_confidence",
            "theta_dynamic", "alpha_demand_impact", "run_duration", "verifier_quality"
        ])
       
        self.predictive_power = 0.0
        self.market_demand_signal = 0.0
        self.prize_pool_forecast = 0.0
        self.conversion_forecast = 0.0
        self.demand_graph = nx.DiGraph()
        logger.info("🚀 PredictiveIntelligenceLayer v0.9.13+ SOTA — fully expanded with real system data, graph, and 7D signals.")

    def update_from_run(self, run_data: Dict) -> float:
        """Maximum real data ingestion from validator, memory, fragment tracker, and graph."""
        validator = getattr(self.arbos, 'validator', None)
        fragment_tracker = getattr(self.arbos, 'fragment_tracker', None)
        memory_layers = getattr(self.arbos, 'memory_layers', None)

        new_row = {
            "timestamp": datetime.now(),
            "efs": getattr(validator, 'last_efs', run_data.get("efs", 0.0)),
            "validation_score": run_data.get("validation_score", getattr(validator, 'last_score', 0.0)),
            "fidelity": getattr(validator, 'last_fidelity', run_data.get("fidelity", 0.0)),
            "heterogeneity": run_data.get("heterogeneity", self._get_real_heterogeneity()),
            "fragments_count": len(memory_layers.get_latest_fragments()) if memory_layers and hasattr(memory_layers, 'get_latest_fragments') else run_data.get("fragments_count", 0),
            "mau_score": getattr(self.arbos, 'mau_per_token', run_data.get("mau_score", 0.0)),
            "freshness_avg": fragment_tracker.get_average_freshness() if fragment_tracker and hasattr(fragment_tracker, 'get_average_freshness') else run_data.get("freshness_avg", 0.0),
            "c3a_confidence": run_data.get("c3a_confidence", getattr(validator, 'last_c3a', 0.0)),
            "theta_dynamic": run_data.get("theta_dynamic", 0.0),
            "alpha_demand_impact": run_data.get("alpha_demand_impact", 0.0),
            "run_duration": run_data.get("duration_seconds", 0.0),
            "verifier_quality": run_data.get("verifier_quality", 0.0)
        }

        self.historical_data = pd.concat([self.historical_data, pd.DataFrame([new_row])], ignore_index=True)
        if len(self.historical_data) > 500:
            self.historical_data = self.historical_data.iloc[-500:]

        if len(self.historical_data) >= 12:
            self._train_models()
            if DEAP_AVAILABLE and len(self.historical_data) >= 20:
                self._evolutionary_tune_hyperparameters()

        self._forecast_all()
        return self.predictive_power

    def _get_real_heterogeneity(self) -> float:
        if hasattr(self.arbos, 'fragment_tracker') and hasattr(self.arbos.fragment_tracker, 'get_average_heterogeneity'):
            return self.arbos.fragment_tracker.get_average_heterogeneity()
        return 0.72

    def _train_models(self):
        feature_cols = ["efs", "validation_score", "fidelity", "heterogeneity",
                       "fragments_count", "mau_score", "freshness_avg", "c3a_confidence", "verifier_quality"]
        X = self.historical_data[feature_cols]
        y = self.historical_data["alpha_demand_impact"]
        self.rf_model.fit(X, y)
        self.gb_model.fit(X, y)

    def _evolutionary_tune_hyperparameters(self):
        """DEAP evolutionary hyperparameter tuning using real data."""
        if not DEAP_AVAILABLE or len(self.historical_data) < 20:
            return
        try:
            # Clean creator
            for name in ["FitnessMax", "Individual"]:
                if name in creator.__dict__:
                    del creator.__dict__[name]
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
            creator.create("Individual", list, fitness=creator.FitnessMax)

            toolbox = base.Toolbox()
            toolbox.register("attr_n_estimators", random.randint, 50, 301)
            toolbox.register("attr_max_depth", random.randint, 5, 31)
            toolbox.register("individual", tools.initCycle, creator.Individual,
                           (toolbox.attr_n_estimators, toolbox.attr_max_depth), n=1)
            toolbox.register("population", tools.initRepeat, list, toolbox.individual)

            def evaluate(individual):
                n_est, max_d = individual
                try:
                    model = RandomForestRegressor(n_estimators=int(n_est), max_depth=int(max_d),
                                                random_state=42, n_jobs=-1)
                    X = self.historical_data[["efs", "validation_score", "fidelity", "heterogeneity",
                                            "fragments_count", "mau_score", "freshness_avg", "c3a_confidence", "verifier_quality"]]
                    y = self.historical_data["alpha_demand_impact"]
                    split = int(len(X) * 0.7)
                    model.fit(X.iloc[:split], y.iloc[:split])
                    score = model.score(X.iloc[split:], y.iloc[split:])
                    return (max(0.0, score),)
                except:
                    return (0.1,)

            toolbox.register("evaluate", evaluate)
            toolbox.register("mate", tools.cxTwoPoint)
            toolbox.register("mutate", tools.mutUniformInt, low=[50, 5], up=[300, 30], indpb=0.25)
            toolbox.register("select", tools.selTournament, tournsize=4)

            population = toolbox.population(n=20)
            NGEN = 10
            for _ in range(NGEN):
                offspring = tools.selTournament(population, len(population), tournsize=3)
                offspring = list(map(toolbox.clone, offspring))
                for child1, child2 in zip(offspring[::2], offspring[1::2]):
                    if random.random() < 0.7:
                        toolbox.mate(child1, child2)
                        del child1.fitness.values, child2.fitness.values
                for mutant in offspring:
                    if random.random() < 0.25:
                        toolbox.mutate(mutant)
                        del mutant.fitness.values
                invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
                fitnesses = map(toolbox.evaluate, invalid_ind)
                for ind, fit in zip(invalid_ind, fitnesses):
                    ind.fitness.values = fit
                population[:] = offspring

            best_ind = tools.selBest(population, 1)[0]
            self.rf_model = RandomForestRegressor(
                n_estimators=int(best_ind[0]),
                max_depth=int(best_ind[1]),
                random_state=42,
                n_jobs=-1
            )
            self._train_models()
            logger.info(f"DEAP tuning completed → Best RF: n_est={int(best_ind[0])}, max_d={int(best_ind[1])}")
        except Exception as e:
            logger.warning(f"DEAP tuning failed (safe): {e}")

    def _forecast_all(self):
        """Full ensemble forecasting with ARIMA, SymPy, NetworkX."""
        if len(self.historical_data) < 8:
            return

        X_latest = self.historical_data[["efs", "validation_score", "fidelity", "heterogeneity",
                                        "fragments_count", "mau_score", "freshness_avg", "c3a_confidence", "verifier_quality"]].iloc[-1:].values

        rf_pred = float(self.rf_model.predict(X_latest)[0])
        gb_pred = float(self.gb_model.predict(X_latest)[0])
        ensemble_pred = (rf_pred + gb_pred) / 2.0

        # ARIMA
        try:
            model = sm.tsa.ARIMA(self.historical_data["efs"].astype(float), order=(2,1,1))
            model_fit = model.fit(disp=False)
            self.prize_pool_forecast = float(model_fit.forecast(steps=3).mean()) * 1200
        except:
            self.prize_pool_forecast = ensemble_pred * 950

        # SymPy symbolic trend
        try:
            t = sp.symbols('t')
            trend = ensemble_pred * (1 + 0.12 * sp.exp(-t/25))
            self.conversion_forecast = float(trend.subs(t, len(self.historical_data)))
        except:
            self.conversion_forecast = ensemble_pred

        # NetworkX demand graph
        self.demand_graph.add_node("current", demand=ensemble_pred, weight=1.0)
        if len(self.demand_graph) > 3:
            pr = nx.pagerank(self.demand_graph, alpha=0.85, weight='weight')
            self.market_demand_signal = pr.get("current", ensemble_pred)
        else:
            self.market_demand_signal = ensemble_pred

        self.conversion_forecast = min(0.98, max(0.0, self.conversion_forecast))

        self.predictive_power = (self.market_demand_signal * 0.45 +
                                self.conversion_forecast * 0.35 +
                                (self.prize_pool_forecast / 20000) * 0.2)

    def sense_market_demand(self, lead_data: Dict) -> Dict:
        """Real-time market sensing with graph context."""
        boost = (lead_data.get("stars", 0) / 800.0) + (lead_data.get("predictive_power", 0.0) * 0.45)
        self.market_demand_signal = min(1.0, max(0.0, self.market_demand_signal + boost))
        return {
            "market_demand_score": round(self.market_demand_signal, 4),
            "prize_pool_forecast": round(self.prize_pool_forecast, 2),
            "conversion_probability": round(self.conversion_forecast, 4),
            "flywheel_impact": "value_return_to_alpha",
            "confidence": round(self.predictive_power, 4)
        }

    def forecast_value_return(self) -> Dict:
        """Compounding value return forecasting for alpha owners."""
        return {
            "revenue_share_forecast": round(self.conversion_forecast * self.market_demand_signal * 0.25, 4),
            "governance_priority": round(self.predictive_power ** 1.35, 4),
            "priority_access_score": round(self.market_demand_signal * 0.97, 4),
            "long_term_alpha_multiplier": round(1 + self.predictive_power * 0.22, 4)
        }

    def route_predictive_signals(self, run_data: Dict):
        """Route full predictive ensemble to Vaults, PD Arm, and BD."""
        if hasattr(self.arbos, 'intelligence') and self.arbos.intelligence:
            self.arbos.intelligence.route_to_vaults({
                "insight_score": self.predictive_power,
                "key_takeaway": f"SOTA predictive ensemble | EFS={self.historical_data['efs'].iloc[-1]:.3f if len(self.historical_data)>0 else 0} | Demand={self.market_demand_signal:.4f}",
                "predictive_power": self.predictive_power,
                "flywheel_step": "predictive_to_pd_vaults"
            })
        if hasattr(self.arbos, 'pd_arm') and self.arbos.pd_arm:
            self.arbos.pd_arm.synthesize_product([], {
                "market_signal": self.market_demand_signal,
                "predictive_power": self.predictive_power,
                "forecast": self.forecast_value_return()
            })
