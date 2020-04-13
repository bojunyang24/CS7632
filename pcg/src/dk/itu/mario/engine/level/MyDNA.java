package dk.itu.mario.engine.level;

import java.util.Random;
import java.util.*;

//Make any new member variables and functions you deem necessary.
//Make new constructors if necessary
//You must implement mutate() and crossover()


public class MyDNA extends DNA
{
	
	public int numGenes = 10; //number of genes
	public final char[] floor = {'a','b','c','d','e','f','g','h','i','j','z'};
	public int highl = 5;
	public final char[] high = {'0','1','2','3','4'};
	public int stuffl = 3;
	public final char[] stuff = {'0','5','6'};
	// Return a new DNA that differs from this one in a small way.
	// Do not change this DNA by side effect; copy it, change the copy, and return the copy.
	public MyDNA mutate ()
	{
		MyDNA copy = new MyDNA();
		//YOUR CODE GOES BELOW HERE
		Random rand = new Random();
		int i = rand.nextInt(this.chromosome.length());
		char mutation = '0';
		if (this.chromosome.charAt(i) >= 'a' || i == 0) {
			// floor
			mutation = floor[rand.nextInt(numGenes)];
		} else if (this.chromosome.charAt(i-1) >= 'a') {
			//high block
			mutation = high[rand.nextInt(highl)];
		} else {
			// stuff
			mutation = stuff[rand.nextInt(stuffl)];
		}
		String copy_chromosome = this.chromosome.substring(0,i) + mutation + this.chromosome.substring(i+1);
		copy.setChromosome(copy_chromosome);
		//YOUR CODE GOES ABOVE HERE
		return copy;
	}
	
	// Do not change this DNA by side effect
	public ArrayList<MyDNA> crossover (MyDNA mate)
	{
		ArrayList<MyDNA> offspring = new ArrayList<MyDNA>();
		//YOUR CODE GOES BELOW HERE
		Random rand = new Random();
		int split = rand.nextInt(this.getLength());
		MyDNA off1 = new MyDNA();
		String off1_chromosome = this.getChromosome().substring(0,split) + mate.getChromosome().substring(split);
		MyDNA off2 = new MyDNA();
		String off2_chromosome = mate.getChromosome().substring(0,split) + this.getChromosome().substring(split);
		off1.setChromosome(off1_chromosome);
		off2.setChromosome(off2_chromosome);
		offspring.add(off1);
		offspring.add(off2);
		//YOUR CODE GOES ABOVE HERE
		return offspring;
	}
	
	// Optional, modify this function if you use a means of calculating fitness other than using the fitness member variable.
	// Return 0 if this object has the same fitness as other.
	// Return -1 if this object has lower fitness than other.
	// Return +1 if this objet has greater fitness than other.
	public int compareTo(MyDNA other)
	{
		int result = super.compareTo(other);
		//YOUR CODE GOES BELOW HERE
		
		//YOUR CODE GOES ABOVE HERE
		return result;
	}
	
	
	// For debugging purposes (optional)
	public String toString ()
	{
		String s = super.toString();
		//YOUR CODE GOES BELOW HERE
		// String out = "";
		// for (int i = 0; i < this.chromosome.length()/this.length; i++) {
		// 	out += s.substring(i * this.length, i * this.length + this.length) + "\n";
		// }
		// return out;
		//YOUR CODE GOES ABOVE HERE
		return s;
	}
	
	public void setNumGenes (int n)
	{
		this.numGenes = n;
	}

}

