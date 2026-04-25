import * as Phaser from 'phaser';
import { gameConfig } from './config';

let game: Phaser.Game | undefined;

export const launchGame = (): Phaser.Game => {
  if (!game) {
    game = new Phaser.Game(gameConfig);
  }

  return game;
};
