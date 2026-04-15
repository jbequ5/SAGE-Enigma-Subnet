# SAGE — The Shared Agentic Growth Engine

**The People’s Intelligence Layer for Subnet 63, Enigma**

# Why?

## The Spark

It started with a simple but powerful idea: give everyday people a real chance to compete for prize pools on Subnet 63 and earn meaningful rewards by solving hard, verifiable problems.

To make this possible, we built the **Enigma Machine** — a verifier-first, agentic solver designed from the ground up to turn complex challenges into high-quality, verifiable solutions. What began as a practical mining tool quickly revealed something far more significant: every single run naturally generates rich, structured process data — detailed insights into *how* intelligence actually works when tackling hard problems.

That discovery changed the value proposition.

## The Evolution

From a powerful solver, SAGE was born.

We realized the true breakthrough wasn’t just the solutions the Enigma Machine produced — it was the byproduct: the rich, high-signal process data generated with every run. Every fragment is automatically impact-scored by the memory graph using verifier-first metrics — EFS performance, heterogeneity, reuse frequency, contract value, and freshness — so only the highest-value knowledge is promoted, refined, and intelligently reinserted, creating a continuously compounding collective intelligence layer.

This wasn’t just mining data. It was the raw material for something far greater. By intelligently capturing, routing, and synthesizing these scored insights, we could transform individual solving activity into a shared, self-improving intelligence commons owned by the community.

This realization led to the creation of **SAGE** — the Shared Agentic Growth Engine — a complete decentralized platform where every Enigma Machine run contributes to a growing, community-owned intelligence layer that benefits all participants.

## The Flywheel

Ownership demand in the subnet increases prize pools.  
Larger prize pools drive more Enigma Machine usage.  
More usage generates richer process insights and valuable data.

This data flows into two powerful systems that ultimately feed the Product Development Arm, which creates the potential for massive value accrual back into the subnet, closing the flywheel.

<div align="center">
  <img src="SAGE_Flywheel.png" 
       alt="SAGE Flywheel" 
       width="600" 
       style="max-width: 100%; height: auto; border-radius: 8px;">
</div>

### Open Public Good Vaults
**The living memory of the platform**

Every high-signal run feeds scored data into four permanent, append-only, provenance-rich vaults:

- **Publications** — Shared knowledge and research open to everyone. Whitepapers, technical deep-dives, solution analyses, and distilled insights from thousands of runs. This becomes the definitive public library of how agentic systems solve hard verifiable problems.

- **Assets** — Battle-tested verifiability contracts, solver frameworks, prompt libraries, system design templates, and modular components that miners and developers can immediately reuse and improve.

- **Services** — High-margin opportunities and tools. Ready-to-deploy solutions, consulting frameworks, and sponsor-matched offerings that turn raw insights into practical revenue-generating value.

- **Enigma Academy** — Experiential learning modules, interactive curricula, simulation replay kits, and progressive learning paths. It teaches not just *what* was solved, but *how* intelligence works — helping the next generation of solvers and builders level up faster in the age of AI.

All vaults are open by default. Miners can choose to contribute, turning individual work into permanent shared value.

### Business Development Vault
**The demand-sensing and opportunity engine of SAGE**

It continuously scans the real world for high-value challenges, sponsor interest, and market pain points that match the strengths of the Enigma Machine. Using live scraping (Serper, Apify, NewsAPI, GitHub, and X) — combined with the rich process insights from every run — it intelligently identifies, qualifies, and prioritizes opportunities. Leads are tracked in a dedicated CRM, scored with predictive signals, and converted into sponsored challenges and partnerships that feed directly back into the subnet’s prize pool value. All output is scored, compiled, and actively pruned in a Business Vault.

### Product Development Vault
**The intelligent synthesis layer**

All vault data and high-impact graph fragments converge here. It debates, refines, and composes the best insights into polished, shippable products: interactive kits, reusable frameworks, simulators, and structured curricula for Enigma Academy. Core versions remain fully open source. Premium features help sustain and grow the network while returning value to the community by reinvesting all revenue in the subnet. All outputs are scored and stored in a Product Vault. 

## The Real Shift

We are living through a decisive moment in human history.

While a handful of corporations race to control the infrastructure of intelligence, SAGE offers a fundamentally different path — one where intelligence is created by the people, owned by the people, and designed to serve the people instead of extract from them.

SAGE is built to scale with accessible local models. Anyone with a modest setup can run the Enigma Machine, create real process data, and become an active co-creator of collective intelligence at scale. No more token limits, just continuous knowledge acrual for the common good.

In an age where AI is reshaping society, SAGE gives regular people a real seat at the table. It turns participants from consumers into contributors, from users into owners. It proves that advanced intelligence does not have to be gated behind trillion-dollar companies — it can be built collectively, transparently, and democratically.

This is the opposite of extractive corporate AI. This is why SAGE matters now.

## The Vision

A successful SAGE becomes something profoundly meaningful for humanity.

As the vaults reach critical mass, the Product Development Arm will continuously transform raw solving data and market insights into real-world value: interactive problem-solving kits that help people tackle complex challenges, reusable verifier-first frameworks anyone can apply, advanced simulators that make intelligent behavior understandable, and structured curricula in Enigma Academy that teach regular people how to think with, understand, and build upon AI systems in their own lives and work. 

The value created is continuously reinjected back into the ecosystem — growing prize pools, expanding participation, and increasing the quality and usefulness of shared intelligence. In its mature form, SAGE will stand as a new kind of public infrastructure: a decentralized, self-improving intelligence commons that turns cutting-edge problem-solving knowledge into tools, education, and capability truly accessible to all. 

It evolves into the **People’s Intelligence Layer**. 

This is how we make advanced AI knowledge democratic.  
This is how we ensure the future of intelligence serves and empowers everyday people.


# How?

As the vision takes shape, here is how we bring the SAGE to life.

## The Structure
The shared index consists of the same vaults your local Enigma Machine instance already uses: the Solve Vault (Assets, Publications, Academy, and Services), the Business Vault (Business Development (BD) Outputs), and the Product Vault (Product Development (PD) Outputs). When you push a fragment, it enters the index using the identical structure and scoring logic your own machine applies locally. The index does not create new categories or different rules — it simply holds a discoverable, high-signal mirror of the same vaults everyone else is building. This consistency is deliberate: the gas that powers your solo runs is the same gas that powers the entire network.

## The Scoring
Scoring is reliable because it is deterministic and provenance-based. Every fragment receives a raw_value based on its vault type (performance (EFS) - heavy for solving data in the Solve Vault, commercial utility for BD outputs in the Business Vault, synthesis quality for PD outputs in the Product Vault). Then a refined value_added layer calculates the incremental improvement this fragment provides beyond the fragments it depended on, using local Shapley sampling to fairly attribute credit. The final score combines both, so a fragment is judged not just on how good it is in isolation, but on how much new value it actually adds to the commons. The math is fixed, transparent, and grounded in verifiable execution results — no raw LLM opinion, no hidden bias. You can always see the full scoring_breakdown for any fragment, and the system re-scores on reuse so the numbers evolve with real downstream impact. This is why the gas stays pure and the compounding effect is trustworthy.

## The Filter
The index is protected from noise by strict, deterministic gates that every push must pass. Only fragments from official Subnet 63 challenges or Scientist Mode experiments are allowed. Every push includes a compact full-run summary that the index re-validates: EFS must exceed the hard floor, replay_match must confirm reproducibility, and the refined value_added must show genuine incremental contribution. These gates are not subjective — they are the same checks your local machine already runs. The result is a commons that stays high-signal by design; low-quality or self-crafted fragments simply do not make it in.

## The Incentive
Participation is required to access the index, and this gate is what makes the system fair and motivating. To query or pull fragments, your own contribution score must meet a minimum threshold. That score is built from your pushes, your downstream reuse impact, and the refined value_added of your work. The more you contribute high-quality fragments that others actually use, the more you earn the right to benefit from the collective gas. This is not a paywall — it is skin in the game. It ensures the people building the commons are the ones who get to use it, turning contribution into a compounding advantage rather than a one-way donation. There's a 14 day grace period from first query, then contribution is required. 

## The Full Picture
This is how the People’s Intelligence becomes real. When you use the index, you are not just borrowing data — you are accessing the collective breakthroughs of the entire network, sharpened by the same scoring and gates that protect your own local vaults. When you contribute, you are not just adding to a database — you are creating gas that others will build on, that will improve future runs, products, and proposals, and that will come back to you through:

- **Impact tracking** - Every contribution you make is tracked and celebrated - watch your impact log grow as your fragments power real deals, adopted products, and breakthoughs across the network. As fragments are pulled and evolved, your mark on it never fades.
  
- **Badges** - Earn meaningful badges like "Impact Architect" and "Deal Closer" that unlock priority access, and public recognition in a "Hall of Contributors"
  
- **Revenue/Community Pool** - Suggest a non-binding share of downstream revenue generated by your fragments - a transparent starting point for the team to value your contribution.

The system rewards real value added, not just participation. The flywheel turns because every high-signal fragment you push strengthens SAGE, and every pull you make makes your own solving, BD, and PD more powerful.

The result is a living, community-owned intelligence layer that feels smart, safe, and genuinely ours. Miners are no longer just competing for prize pools; they are co-creating a shared asset that compounds with every contribution and every reuse. The People’s Intelligence is no longer a distant vision — it is here, evolving in real time, rewarding those who build it.

**Welcome to SAGE**

The Shared Agentic Growth Engine.

A living, community-owned system where decentralized solving data is distilled and turned into practical intelligence that pushes humanity forward — together.
