package dk.itu.mario.engine.level.generator;

import java.util.*;

import dk.itu.mario.MarioInterface.Constraints;
import dk.itu.mario.MarioInterface.GamePlay;
import dk.itu.mario.MarioInterface.LevelGenerator;
import dk.itu.mario.MarioInterface.LevelInterface;
import dk.itu.mario.engine.level.Level;
import dk.itu.mario.engine.level.MyLevel;
import dk.itu.mario.engine.level.MyDNA;

import dk.itu.mario.engine.PlayerProfile;

import dk.itu.mario.engine.sprites.SpriteTemplate;
import dk.itu.mario.engine.sprites.Enemy;

public class MyLevelGenerator{

	public boolean verbose = false; //print debugging info
	public boolean v = false; //print debugging info

	// MAKE ANY NEW MEMBER VARIABLES HERE

	// Called by the game engine.
	// Returns the level to be played.
	public Level generateLevel(PlayerProfile playerProfile)
	{
		// Call genetic algorithm to optimize to the player profile
		MyDNA dna = this.geneticAlgorithm(playerProfile);

		// Post process
		dna = this.postProcess(dna);

		// Convert the solution to the GA into a Level
		MyLevel level = new MyLevel(dna, LevelInterface.TYPE_OVERGROUND);

		if (this.v) {
			// System.out.println("Solution: " + dna + " fitness: " + playerProfile.evaluateLevel(level));
			System.out.println("fitness: " + playerProfile.evaluateLevel(level));
		}
		if (this.verbose) {
			// System.out.println("Solution: " + dna + " fitness: " + playerProfile.evaluateLevel(level));
			System.out.println("fitness: " + playerProfile.evaluateLevel(level));
		}

		return (Level)level;
	}

	// Genetic Algorithm implementation
	private MyDNA geneticAlgorithm (PlayerProfile playerProfile)
	{
		// Set the population size
		int populationSize = getPopulationSize();

		// Make the population array
		ArrayList<MyDNA> population = new ArrayList<MyDNA>();

		// Make the solution, which is initially null
		MyDNA solution = null;

		// Generate a random population
		for (int i=0; i < populationSize; i++) {
			MyDNA newIndividual = this.generateRandomIndividual();
			newIndividual.setFitness(this.evaluateFitness(newIndividual, playerProfile));
			population.add(newIndividual);
		}
		if (this.verbose) {
			System.out.println("Initial population:");
			printPopulation(population);
		}

		// Iteration counter
		int count = 0;

		// Iterate until termination criteria met
		while (!this.terminate(population, count)) {
			// Make a new, possibly larger population
			ArrayList<MyDNA> newPopulation = new ArrayList<MyDNA>();

			// Keep track of individual's parents (for this iteration only)
			Hashtable parents = new Hashtable();

			// Mutuate a number of individuals
			ArrayList<MyDNA> mutationPool = this.selectIndividualsForMutation(population);
			for (int i=0; i < mutationPool.size(); i++) {
				MyDNA parent = mutationPool.get(i);
				// Mutate
				MyDNA mutant = parent.mutate();
				// Evaluate fitness
				double fitness = this.evaluateFitness(mutant, playerProfile);
				mutant.setFitness(fitness);
				// Add mutant to new population
				newPopulation.add(mutant);
				// Create a list of parents and remember it in a hash
				ArrayList<MyDNA> p = new ArrayList<MyDNA>();
				p.add(parent);
				parents.put(mutant, p);
			}


			// Do Crossovers
			for (int i=0; i < this.numberOfCrossovers(); i++) {
				// Pick two parents
				MyDNA parent1 = this.pickIndividualForCrossover(newPopulation, null);
				MyDNA parent2 = this.pickIndividualForCrossover(newPopulation, parent1);

				if (parent1 != null && parent2 != null) {
					// Crossover produces one or more children
					ArrayList<MyDNA> children = parent1.crossover(parent2);

					// Add children to new population and remember their parents
					for (int j=0; j < children.size(); j++) {
						// Get a child
						MyDNA child = children.get(j);
						// Evaluate fitness
						double fitness = this.evaluateFitness(child, playerProfile);
						child.setFitness(fitness);
						// Add it to new population
						newPopulation.add(child);
						// Create a list of parents and remember it in a hash
						ArrayList<MyDNA> p = new ArrayList<MyDNA>();
						p.add(parent1);
						p.add(parent2);
						parents.put(child, p);
					}
				}

			}

			// Cull the population
			// There is more than one way to do it.
			if (this.competeWithParentsOnly()) {
				population = this.competeWithParents(population, newPopulation, parents);
			}
			else {
				population = this.globalCompetition(population, newPopulation);
			}

			//increment counter
			count = count + 1;

			if (this.v) {
				MyDNA best = this.getBestIndividual(population);
				System.out.println("" + count + ": fitness: " + best.getFitness());
			}
			if (this.verbose) {
				MyDNA best = this.getBestIndividual(population);
				System.out.println("" + count + ": Best: " + best + " fitness: " + best.getFitness());
			}
		}

		// Get the winner
		solution = this.getBestIndividual(population);

		return solution;
	}

	// Create a random individual.
	private MyDNA generateRandomIndividual ()
	{
		MyDNA individual = new MyDNA();
		// YOUR CODE GOES BELOW HERE
		int numGenes = 10; //number of genes
		char[] floor = {'a','b','c','d','e','f','g','h','i','j','z'};
		int highl = 5;
		char[] high = {'0','1','2','3','4'};
		int stuffl = 3;
		char[] stuff = {'0','5','6'};
		String chromosome = "";
		int i = 0;
		char prev = 'a';
		int gap = 0;
		Random rand = new Random();
		while (i < 205) {
			int diff = rand.nextInt(3);
			if (rand.nextInt(10) < 3 && gap < 3) {
				chromosome += 'z' + "" + high[rand.nextInt(highl)] + stuff[rand.nextInt(stuffl)];
				gap++;
			} else {
				gap = 0;
				if (prev <= 'c') {
					prev = (char) ((int) prev + diff);
				} else if (prev >= 'h') {
					prev = (char) ((int) prev - diff);
				} else {
					if (rand.nextInt(10) < 5) {
						prev = (char) ((int) prev + diff);
					} else {
						prev = (char) ((int) prev - diff);
					}
				}
				chromosome += prev + "" + high[rand.nextInt(highl)] + stuff[rand.nextInt(stuffl)];
			}
			i++;
		}
		individual.setChromosome(chromosome);
		// YOUR CODE GOES ABOVE HERE
		return individual;
	}

	// Returns true if the genetic algorithm should terminate.
	private boolean terminate (ArrayList<MyDNA> population, int count)
	{
		boolean decision = false;
		// YOUR CODE GOES BELOW HERE
		for (int i = 0; i < population.size(); i++) {
			if (population.get(i).getFitness() >= 0.80) {
				return true;
			}
		}
		if (count > 250) {
			return true;
		}
		// YOUR CODE GOES ABOVE HERE
		return decision;
	}

	// Return a list of individuals that should be copied and mutated.
	private ArrayList<MyDNA> selectIndividualsForMutation (ArrayList<MyDNA> population)
	{
		ArrayList<MyDNA> selected = new ArrayList<MyDNA>();
		// YOUR CODE GOES BELOW HERE
		Random rand = new Random();
		for (int i = 0; i < population.size(); i++) {
			if (rand.nextInt(10) < 7) {
				selected.add(population.get(i));
			}
		}
		// YOUR CODE GOES ABOVE HERE
		return selected;
	}

	// Returns the size of the population.
	private int getPopulationSize ()
	{
		int num = 1; // Default needs to be changed
		// YOUR CODE GOES BELOW HERE
		num = 200;
		// YOUR CODE GOES ABOVE HERE
		return num;
	}

	// Returns the number of times crossover should happen per iteration.
	private int numberOfCrossovers ()
	{
		int num = 0; // Default is no crossovers
		// YOUR CODE GOES BELOW HERE
		num = getPopulationSize()/2;
		// YOUR CODE GOES ABOVE HERE
		return num;

	}

	// Pick one of the members of the population that is not the same as excludeMe
	private MyDNA pickIndividualForCrossover (ArrayList<MyDNA> population, MyDNA excludeMe)
	{
		MyDNA picked = null;
		Boolean selected = false;
		// YOUR CODE GOES BELOW HERE
		Random rand = new Random();
		while (!selected) {
			picked = population.get(rand.nextInt(population.size()));
			if (picked != excludeMe) {
				selected = true;
			}
		}
		// YOUR CODE GOES ABOVE HERE
		if (picked == excludeMe) {
			return null;
		}
		else {
			return picked;
		}
	}

	// Returns true if children compete to replace parents.
	// Retursn false if the the global population competes.
	private boolean competeWithParentsOnly ()
	{
		boolean doit = false;
		// YOUR CODE GOES BELOW HERE
		// doit = true;
		// YOUR CODE GOES ABOVE HERE
		return doit;
	}

	// Determine if children are fitter than parents and keep the fitter ones.
	private ArrayList<MyDNA> competeWithParents (ArrayList<MyDNA> oldPopulation, ArrayList<MyDNA> newPopulation, Hashtable parents)
	{
		ArrayList<MyDNA> finalPopulation = new ArrayList<MyDNA>();
		// YOUR CODE GOES BELOW HERE

		// YOUR CODE GOES ABOVE HERE
		if (finalPopulation.size() != this.getPopulationSize()) {
			throw new IllegalStateException("Population not the correct size.");
		}
		return finalPopulation;
	}
	
	Comparator<MyDNA> c = new Comparator<MyDNA>() {
		public int compare(MyDNA a, MyDNA b) {
			if (a.getFitness() == b.getFitness()) {
				return 0;
			}
			else if (a.getFitness() > b.getFitness()) {
				return -1;
			}
			else {
				return 1;
			}
		}
	};

	// Combine the old population and the new population and return the top fittest individuals.
	private ArrayList<MyDNA> globalCompetition (ArrayList<MyDNA> oldPopulation, ArrayList<MyDNA> newPopulation)
	{
		ArrayList<MyDNA> finalPopulation = new ArrayList<MyDNA>();
		// YOUR CODE GOES BELOW HERE
		oldPopulation.addAll(newPopulation);
		// Collections.sort(oldPopulation);
		oldPopulation.sort(this.c);
		int i = 0;
		while (finalPopulation.size() != this.getPopulationSize()) {
			finalPopulation.add(oldPopulation.get(i));
			i++;
		}
		// YOUR CODE GOES ABOVE HERE
		if (finalPopulation.size() != this.getPopulationSize()) {
			throw new IllegalStateException("Population not the correct size.");
		}
		return finalPopulation;
	}
	
	
	// Return the fittest individual in the population.
	private MyDNA getBestIndividual (ArrayList<MyDNA> population)
	{
		MyDNA best = population.get(0);
		double bestFitness = Double.NEGATIVE_INFINITY;
		for (int i=0; i < population.size(); i++) {
			MyDNA current = population.get(i);
			double currentFitness = current.getFitness();
			if (currentFitness > bestFitness) {
				best = current;
				bestFitness = currentFitness;
			}
		}
		return best;
	}

	// Changing this function is optional.
	private double evaluateFitness (MyDNA dna, PlayerProfile playerProfile)
	{
		double fitness = 0.0;
		// YOUR CODE GOES BELOW HERE
		MyLevel level = new MyLevel(dna, LevelInterface.TYPE_OVERGROUND);
		fitness = playerProfile.evaluateLevel(level);
		// YOUR CODE GOES ABOVE HERE
		return fitness;
	}

	private MyDNA postProcess (MyDNA dna)
	{
		// YOUR CODE GOES BELOW HERE
		for (int x = 0; x < 203; x++) {
			String curr = dna.getChromosome().substring(x * 3, x * 3 + 3);
			String next = dna.getChromosome().substring((x+1) * 3, (x+1) * 3 + 3);
			if ((next.charAt(0) != 'z' || curr.charAt(0) == 'z') && next.charAt(0) - curr.charAt(0) > 5) {
				dna.setChromosome(dna.getChromosome().substring(0, x*3) + curr + ((char) ((int) next.charAt(0) - 1)) + next.substring(1) + dna.getChromosome().substring((x+2)*3));
			}
			// if (curr.charAt(1) == '3') {
			// 	char replace = dna.getChromosome().charAt(x*3+6);
			// 	if (replace > 'a' && replace <= 'j' && replace - dna.getChromosome().charAt(x*3) > 2) {
			// 		replace = (char) ((int) replace - 1);
			// 		dna.setChromosome(dna.getChromosome().substring(0, x*3+6) + replace + dna.getChromosome().substring(x*3+7));
			// 	}
			// }
		}
		for (int x = 0; x < 200; x++) {
			int toobig = 0;
			for (int xx = x; xx < x + 4; xx++) {
				if (dna.getChromosome().charAt(xx*3) == 'z') {
					toobig++;
				}
				if (toobig == 4) {
					dna.setChromosome(dna.getChromosome().substring(0, xx*3) + dna.getChromosome().substring((xx-5)*3, ((xx-5)*3) + 3) + dna.getChromosome().substring((xx+1)*3));
				}
			}
		}
		// YOUR CODE GOES ABOVE HERE
		return dna;
	}

	//for this to work, you must implement MyDNA.toString()
	private void printPopulation (ArrayList<MyDNA> population)
	{
		for (int i=0; i < population.size(); i++) {
			MyDNA dna = population.get(i);
			System.out.println("Individual " + i + ": " + dna + " fitness: " + dna.getFitness());
		}
	}

	// MAKE ANY NEW MEMBER FUNCTIONS HERE

}
